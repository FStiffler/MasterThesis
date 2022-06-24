import parameters
from pulp import PULP_CBC_CMD
import numpy as np
import pandas as pd
import pulp as pl
import random as ra
import itertools as it


def get_all_player_data():
    """
    Description:
    Get all player information as data frame

    Returns:
    allPlayersData (dataframe): Dataframe with information about all players
    """
    allPlayersData = pd.DataFrame(
        data=np.column_stack((parameters.allPlayers, parameters.allPlayerSkills, parameters.allPlayerSalaries)),
        # arrays as columns
        columns=["player", "skill", "salary"]
    )
    allPlayersData = allPlayersData.astype({"player": int, 'salary': int})  # change player to integer

    return allPlayersData


def skill_maximization(playerPool, teamBudget):
    """
    Description:
    Function which allows team to select players while maximizing skill given a team size and budget constraint

    Input:
    playerPool (PlayerPool): A player pool of object PlayerPool
    teamBudget (int): The budget constraint for a particular team used to optimize skill

    Returns:
    selectedPlayers (pandas dataframe): A pandas dataframe which includes data about selected players by team
    """

    # initialize variables
    playerData = playerPool.allPlayersData  # get data from all players as data frame
    players = playerPool.get_all_players()  # get all players as list
    skills = playerPool.get_all_player_skills()  # get skill levels of all players as list
    salaries = playerPool.get_all_player_salaries()  # get salaries of all players as list
    binaries = [pl.LpVariable(  # initialise list of binary variables, one for each player
        "d_" + str(players[i]),  # name the variables: d_player
        cat="Binary") for i in range(len(players))]  # iterate through all players

    # initialize problem
    prob = pl.LpProblem(name="BestTeam", sense=-1)  # sense=-1 indicates maximization problem

    # define objective function
    prob += pl.lpSum(binaries[i] * skills[i] for i in range(len(players)))  # maximize skill

    # define the constraints
    prob += pl.lpSum(binaries[i] for i in range(len(players))) == parameters.teamSize  # team size constraint
    prob += pl.lpSum(binaries[i] * salaries[i] for i in range(len(players))) <= teamBudget  # budget constraint

    # solve problem to obtain the optimal solution (best team)
    prob.solve(solver=PULP_CBC_CMD(msg=False))

    # initialize empty lists for the variable names and solution values
    variables = []
    solutions = []

    # write each variable name and solution value to the lists
    for v in prob.variables():
        variable = v.name
        solution = v.varValue
        variables.append(variable)  # append variable name to existing list
        solutions.append(solution)  # append solution value to existing list

    # obtain selected players
    solutions = np.array(solutions).astype(int)  # define solution values as integers (binary)
    solutionDF = pd.DataFrame(  # define a data frame with all variables and according optimal values
        data=np.array([variables, solutions]).T,  # .T makes sure to convert the 2xn matrix to a nx2 matrix
        columns=['Variable', 'Optimal Value']
    )
    solutionDF['Optimal Value'] = solutionDF['Optimal Value'].astype(int)  # define column as binary
    solutionDF = solutionDF[solutionDF['Optimal Value'] == 1]  # filter selected players
    selectedPlayers = playerData.loc[  # create data frame with information about selected players
        playerData['player'].isin(  # filter players in array
            np.array(
                solutionDF.Variable.str.split('_').tolist()  # extract player player from variable name
            )[:, 1].astype(int)  # select column with player and define them as integer
        )
    ]

    # assert that constraints hold since the solver does not throw an error when not converging to a solution
    assert len(selectedPlayers) == parameters.teamSize
    assert selectedPlayers.salary.sum() <= teamBudget

    # return selected team
    return selectedPlayers


def identify_conflicts(leagueObject):
    """
    Description:
    Function to identify players who multiple teams are interested in

    Input:
    leagueObject (League): The initialised league object of class League

    Returns:
    conflicts (dict): A dictionary showing the conflicting player as key and all interested teams as values in a list
    noConflicts (dict): A dictionary showing the non-conflicting player as key and the interested team as value in a list
    """
    # get required team information
    optimalPlayers = leagueObject.optimalPlayers
    optimalPlayersSet = leagueObject.optimalPlayersSet

    # create a data frame from dictionary
    optimalPlayersDF = pd.DataFrame(optimalPlayers)

    # pivot to long format
    optimalPlayersDF = pd.melt(optimalPlayersDF,
                               value_vars=optimalPlayersDF.columns,
                               var_name='team',
                               value_name='player')

    # initialise empty dictionaries to be filled with observed conflicts and non conflicts
    conflicts = {}
    noConflicts = {}

    # loop over all players to identify conflicts
    for player in optimalPlayersSet:

        # extract all teams interested in the same player
        interestedTeams = optimalPlayersDF.loc[optimalPlayersDF['player'] == player]

        # if more than one team are interested in one player
        if len(interestedTeams) > 1:

            # add player as key and list of interested teams as value to the conflicts dictionary
            conflicts[player] = interestedTeams.team.tolist()

        # if only one team wants to acquire a player
        else:

            # add player as key and list containing interested team as value to the non conflicts dictionary
            noConflicts[player] = interestedTeams.team.tolist()

    # return dictionaries
    return conflicts, noConflicts


def shuffle_conflicts(conflicts):
    """
    Description:
    Function to shuffle order of conflicts to be solved

    Input:
    conflicts (dict): A dictionary which contains all players as key and a list of interested teams as values

    Returns:
    shuffledConflicts (dict): The same dictionary as input but now with shuffled conflicts (changed order)
    """

    # create list of conflict items where each item consists of a tuple with the conflicting player and a list of teams
    conflictItems = list(conflicts.items())

    # shuffle the tuples
    ra.shuffle(conflictItems)

    # create a shuffled dictionary
    shuffledConflicts = dict(conflictItems)

    # return
    return shuffledConflicts


def assign_player(leagueObject, player, team):
    """
    Description:
    Function to assign a player to a specific team

    Input:
    leagueObject (League): The initialised league object of class League
    derived from an object with class League
    player (int): The new player to be added to the already existing selection of players of the team
    team (str): The team to which the new player is to be assigned

    Returns:
    finalPlayerSelection (dict): Updates and returns final player selection
    """
    # get required team information
    finalPlayerSelection = leagueObject.finalPlayerSelection

    # append the new player to a list of existing players for a team
    finalPlayerSelection[team].append(player)

    # return
    return finalPlayerSelection


def update_team_info(leagueObject, allPlayersData):
    """
    Description:
    Function to update the team info of all teams

    Input:
    leagueObject (League): The initialised league object of class League
    allPlayersData (dataframe): A dataframe with information about all players in the player pool created when player pool was initialised

    Returns:
    teamData (dataframe): Updates and returns information about the teams in a dataframe
    """
    # get required team information
    finalPlayerSelection = leagueObject.finalPlayerSelection
    teamData = leagueObject.teamData

    # define variables to obtain and summarize
    variableName = ['salary', 'skill']

    for variable in variableName:
        # obtain defined variable values for every selected player
        variableDict = {team: allPlayersData.loc[allPlayersData['player'].isin(players), variable].values.tolist() for
                        (team, players) in finalPlayerSelection.items()}

        # calculate sum of variable value
        variableSumDict = {team: sum(value) for (team, value) in variableDict.items()}

        # if variable is 'salary'
        if variable == 'salary':
            # append a list of all team salaries to the column 'payroll'
            teamData['payroll'] = list(variableSumDict.values())

        if variable == 'skill':
            # append a list of all team salaries to the column 'totalSkill'
            teamData['totalSkill'] = list(variableSumDict.values())

    # return
    return teamData


def player_chooses_team(interestedTeams):
    """
    Description:
    Function representing the decision rule if a player has to choose between teams

    Input:
    interestedTeams (list): list of teams interested in player

    Returns:
    decision (str): The team team the player has chosen
    """

    # let player decide for one team
    decision = ra.choice(interestedTeams)

    # return player decision
    return decision


def teams_choose_replacement(player, team, playerPool, leagueObject):
    """
    Description:
    Function representing the replacement decision by teams which were not picked by a player they considered optimal

    Input:
    player (int): The player who did not join the team and thus needs to be replaced
    team (str): The team which has to decide which player to choose now for replacement
    playerPool (PlayerPool): The initialised player pool object
    leagueObject (League): The initialised league object of class League

    Returns:
    replacementPlayer (int): The replacement player (number)
    """
    # get required team information
    teamData = leagueObject.teamData

    # get required player information
    allPlayersData = playerPool.allPlayersData
    availablePlayersData = playerPool.availablePlayersData.copy()

    # filter player skill from player to be replaced
    playerSkill = allPlayersData.loc[allPlayersData['player'] == player, 'skill'].values[0]

    # add new column with absolut skill gab to data about still available players
    availablePlayersData['skillGab'] = abs(playerSkill - availablePlayersData['skill'])

    # order available player data according to skill gab
    availablePlayersData.sort_values('skillGab', inplace=True, ignore_index=True)

    # identify current team payroll
    teamPayroll = teamData.loc[teamData['team'] == team, 'payroll'].values[0]

    # identify team budget
    teamBudget = teamData.loc[teamData['team'] == team, 'budget'].values[0]

    # initialise index for loop
    index = 0

    # while index is smaller then length of dataframe containing replacement players
    while index < len(availablePlayersData):

        # identify a replacement player in increasing order of skill gab
        replacementPlayerInfo = availablePlayersData.iloc[index,]

        # identify salary of replacement player
        replacementPlayerSalary = replacementPlayerInfo['salary']

        # if addition of player salary to team payroll would lead to a violation of team budget
        if teamPayroll + replacementPlayerSalary > teamBudget:

            # increase index by one to try next player in order
            index += 1

            # raise exception if there is no other player left and the budget constraint is violated
            if index == len(availablePlayersData):
                raise Exception("""
                Problem finding replacement player -
                All the available players serving as potential replacements have salaries violating budget 
                constraint when added to the team
                """)

        # if there is no violation
        else:

            # identify replacement player by player number
            replacementPlayer = int(replacementPlayerInfo['player'])

            # break loop
            break

    # return id of chosen player
    return replacementPlayer


def no_duplicates(finalPlayerSelection):
    """
    Description:
    Function to check if any player appears twice in the final teams

    Input:
    finalPlayerSelection (dict): dictionary showing final player selection of teams

    Returns:
    state (str): If there are no duplicates True is returned otherwise False is returned
    """

    # create nested list where the lists consists of one list of players per team
    nestedList = list(finalPlayerSelection.values())

    # flatten list so that each player is single list element
    flatList = [player for team in nestedList for player in team]

    # check for duplicates
    state = (len(set(flatList)) == len(flatList))

    # return player decision
    return state


def simulate_game(homeTeam, skillHomeTeam, awayTeam, skillAwayTeam, leagueObject, seasonPhase, placementGame=False):
    """
    Description:
    Function to simulate one game

    Input:
    homeTeam (str): Name of first home team
    skillHomeTeam (float): Total skill of home team
    awayTeam (str): Name of away team
    skillAwayTeam (float): Total skill of away team
    leagueObject (League): The initialised league of object League
    seasonPhase (int): seasonPhase (int): Integer defining in which phase of season we are, 0 = Regular Season,
    1 or 2 = pre playoffs and playoffs respectively
    placementGame (bool): Indicates if the game to be simulated is a placement game, False = no placement game,
    True = placement game, default is False

    Returns:
    winner (str): Name of winner
    """

    # calculate winning-percentage of home team in pairing
    winPercentageHome = skillHomeTeam / (skillHomeTeam + skillAwayTeam)

    # if the game is not a placement game
    if not placementGame:

        # calculate earned revenue of home team in this game
        leagueObject.calculate_game_revenue(homeTeam, winPercentageHome, seasonPhase)

    # determine whether or not home team wins
    homeVictory = ra.choices([True, False], [winPercentageHome, 1 - winPercentageHome])[0]

    # if home team in pairing has won
    if homeVictory:

        # return name of home team
        return homeTeam

    # if away team in pairing has won
    else:

        # return name of away team
        return awayTeam


def placement_games(equalTeams, leagueObject):
    """
    Description:
    Function to simulate placement games where teams replay each other for ranking when they are equally ranked and have
    a balanced score in direct  confrontation

    Input:
    equalTeams (list): List of all teams which have same  number of wins
    leagueObject (League): The initialised league object of class League

    Returns:
    finalPlacementRanking (dataframe): Dataframe with a ranking of the placement games
    """

    # initialise skillDictionary
    skillDictionary = leagueObject.get_skill_dictionary()

    # initialise placement decision status
    placementDecision = False

    # while no decision in placement games
    while not placementDecision:

        # initialise empty ranking
        placementRanking = pd.DataFrame({'rank': [0] * len(equalTeams),
                                         'team': equalTeams,
                                         'wins': [0] * len(equalTeams)
                                         })

        # initialise record of all game outcomes
        placementGamesRecord = pd.DataFrame({'homeTeam': [], 'awayTeam': [], 'winner': []})

        # create each possible team pairing for placement round, one game against each opponent, one team is away one home but it does not affect revenue
        placementPairings = list(it.combinations(equalTeams, 2))

        # for each pairing
        for pairing in placementPairings:
            # extract skills of both teams
            homeTeam = pairing[0]
            awayTeam = pairing[1]
            skillHomeTeam = skillDictionary[homeTeam]
            skillAwayTeam = skillDictionary[awayTeam]

            # simulate game between team pairing
            winner = simulate_game(homeTeam, skillHomeTeam, awayTeam, skillAwayTeam, leagueObject,
                                   parameters.regularSeason, placementGame=True)

            # add a win to the winning team's record
            placementRanking.loc[placementRanking['team'] == winner, 'wins'] += 1

            # sort ranking
            placementRanking.sort_values('wins', ignore_index=True, inplace=True, ascending=False)

            # newPlacementRecord
            newRecord = pd.DataFrame(
                {'homeTeam': [homeTeam], 'awayTeam': [awayTeam], 'winner': [winner]})

            # concat new record with record of previous games
            placementGamesRecord = pd.concat([placementGamesRecord, newRecord], ignore_index=True)

        # recursively call solve_ranking_conflicts
        finalPlacementRanking = solve_ranking_conflicts(placementRanking, placementGamesRecord, skillDictionary)

        # if ranking is resolved
        if len(set(finalPlacementRanking['rank'].tolist())) == len(equalTeams):
            # return final ranking
            return finalPlacementRanking


def solve_ranking_conflicts(ranking, record, leagueObject):
    """
    Description:
    Function to solve ranking conflicts when two teams have same number of wins (and thus winning percentage)

    Input:
    ranking (dataframe): Dataframe containing ranking with calculated winning percentages
    record (dataframe): Dataframe containing the record of all games played
    leagueObject (League): The initialised league object of class League

    Returns:
    resolvedRanking (dataframe): Dataframe with unambiguous ranking for all teams
    """
    # initialise row
    row = 0

    # go through ranking row by row from top down
    while row < len(ranking):

        # extract number of wins
        winNumber = ranking.loc[row, 'wins']

        # if no other team had the same number of wins
        if sum(ranking['wins'] == winNumber) == 1:

            # assign rank to the team
            ranking.iloc[row, 0] = row + 1

            # go to next iteration
            row += 1

        # if there are other teams with the same number of wins
        else:

            # identify all teams with same number of wins
            equalTeams = ranking.loc[ranking['wins'] == winNumber, 'team'].tolist()

            # extract all direct games between these teams
            directRecord = record.loc[(record['homeTeam'].isin(equalTeams)) & (record['awayTeam'].isin(equalTeams))]

            # calculate the direct wins by each team
            directWins = [len(directRecord.loc[directRecord['winner'] == team]) for team in equalTeams]

            # if all teams have the exact same number of direct against each other
            if len(set(directWins)) == 1:

                # play placement games
                placementRanking = placement_games(equalTeams, leagueObject)

                # for each entry in resolved direct ranking
                for index in range(len(placementRanking)):
                    # identify team
                    team = placementRanking.loc[index, "team"]

                    # assign this team the correct ranking
                    ranking.loc[ranking['team'] == team, 'rank'] = row + 1

                    # increase row by 1
                    row += 1

            # if not all teams have an equal number of wins against each other
            else:
                # initialise empty ranking to fill with direct record among equal teams
                directRanking = pd.DataFrame({'rank': [0] * len(equalTeams),
                                              'team': equalTeams,
                                              'wins': directWins})

                # sort direct ranking dataframe based on wins
                directRanking.sort_values('wins', ignore_index=True, inplace=True, ascending=False)

                # recursively call this function with direct rankin, direct record and leagueObject
                resolvedDirectRanking = solve_ranking_conflicts(directRanking, directRecord, leagueObject)

                # for each entry in resolved direct ranking
                for index in range(len(resolvedDirectRanking)):
                    # identify team
                    team = resolvedDirectRanking.loc[index, "team"]

                    # assign this team the correct ranking
                    ranking.loc[ranking['team'] == team, 'rank'] = row + 1

                    # increase row by 1
                    row += 1

    # Sort teams based on resolved ranking
    ranking.sort_values('rank', inplace=True, ignore_index=True)

    # return resolved ranking final
    return ranking


def simulate_regular_season(leagueObject):
    """
    Description:
    Function to simulate an entire regular season based on team skills

    Input:
    leagueObject (League): The initialised league object of class League

    Returns:
    ranking (dataframe): Return ranking of regular season
    """

    # create skill dictionary
    skillDictionary = leagueObject.get_skill_dictionary()

    # initialise empty ranking
    ranking = pd.DataFrame({'rank': [0] * len(parameters.teams),
                            'team': list(skillDictionary.keys()),
                            'skill': list(skillDictionary.values()),  # add column skill to dataframe
                            'wins': [0] * len(parameters.teams),
                            'games': [0] * len(parameters.teams),
                            'winningPercentage': ['-'] * len(parameters.teams)})

    # initialise record of all game outcomes
    record = pd.DataFrame({'homeTeam': [], 'awayTeam': [], 'winner': []})

    # create pairings that each team faces any other team at home and away (first team is home team)
    pairings = list(it.permutations(parameters.teams, 2))

    # for each pairing
    for pairing in pairings:

        # extract names and skills of both teams
        homeTeam = pairing[0]
        awayTeam = pairing[1]
        skillHomeTeam = skillDictionary[homeTeam]
        skillAwayTeam = skillDictionary[awayTeam]

        # initialise game count
        game = 1

        # as long as not 2 games have been played (two home games against each opponent)
        while game < 3:
            # simulate game between team pairing
            winner = simulate_game(homeTeam, skillHomeTeam, awayTeam, skillAwayTeam,
                                   leagueObject, parameters.regularSeason)

            # add a win to the winning team's record
            ranking.loc[ranking['team'] == winner, 'wins'] += 1

            # create a new record for this game
            newRecord = pd.DataFrame(
                {'homeTeam': [homeTeam], 'awayTeam': [awayTeam], 'winner': [winner]})

            # concat new record with record of previous games
            record = pd.concat([record, newRecord], ignore_index=True)

            # increase the number of games for both teams by 1
            ranking.loc[ranking['team'].isin(pairing), 'games'] += 1

            # end of game 1
            game += 1

    # calculate winning percentage
    ranking['winningPercentage'] = ranking['wins'] / ranking['games']

    # sort ranking
    ranking.sort_values('winningPercentage', ascending=False, inplace=True, ignore_index=True)

    # team revenues before resolving ranking conflicts
    oldTeamRevenues = leagueObject.get_team_revenues()

    # resolve ranking conflicts
    resolvedRanking = solve_ranking_conflicts(ranking, record, leagueObject)

    # team revenues after resolving ranking conflicts
    newTeamRevenues = leagueObject.get_team_revenues()

    # assert that revenues have not changed when ranking conflicts were resolved
    assert all([oldTeamRevenues[i] == newTeamRevenues[i] for i in range(len(oldTeamRevenues))])

    # return ranking
    return resolvedRanking


def simulate_playoff_round(leagueObject, teamPairings, playoffsType):
    """
    Description:
    Function to simulate one round of a certain playoff type (pre playoffs, playoffs)

    Input:
    leagueObject (League): The initialised league object of class League
    teamPairings (list): List of tuples with team pairings for the round
    playoffsType (int): Integer indicating which type of playoffs is to be played, 1 = pre playoffs -> best of three,
    2 = playoffs ->best of seven

    Returns:
    winningTeams (list): List of teams which have won their respective pairing
    """
    # initialise skillDictionary
    skillDictionary = leagueObject.get_skill_dictionary()

    # if pre playoffs are to be played
    if playoffsType == 1:
        # create overall pre playoff record
        prePlayoffsRecord = pd.DataFrame({'higherRankedTeam': [], 'lowerRankedTeam': [], 'winner': []})

        # for each pairing in pre playoffs
        for pairing in teamPairings:

            # determine higher ranked team
            higherRankedTeam = pairing[0]

            # determine lower ranked team
            lowerRankedTeam = pairing[1]

            # create a within playoff pairing record of home and away games
            prePlayoffPairingRecord = pd.DataFrame({
                'homeTeam': [i for i in 1*[higherRankedTeam, lowerRankedTeam]+[higherRankedTeam]],
                'awayTeam': [i for i in 1*[lowerRankedTeam, higherRankedTeam]+[lowerRankedTeam]],
                'winner': ['']*3})

            # initialise game count
            game = 1

            # as long as not 4 games have been played
            while game < 4:

                # get index of game
                gameIndex = game - 1

                # define teams in that game
                homeTeam = prePlayoffPairingRecord.loc[gameIndex, 'homeTeam']
                awayTeam = prePlayoffPairingRecord.loc[gameIndex, 'awayTeam']
                skillHomeTeam = skillDictionary[homeTeam]
                skillAwayTeam = skillDictionary[awayTeam]

                # simulate game between teams
                winner = simulate_game(homeTeam, skillHomeTeam, awayTeam, skillAwayTeam,
                                       leagueObject, parameters.prePlayoff)

                # write winner to record
                prePlayoffPairingRecord.loc[gameIndex, 'winner'] = winner

                # check if higher ranked team in pairing has already won pre playoff round
                if len(prePlayoffPairingRecord.loc[prePlayoffPairingRecord['winner'] == higherRankedTeam]) == 2:

                    # create new playoff record for this pairing
                    newPrePlayoffsRecord = pd.DataFrame(
                        {'higherRankedTeam': [higherRankedTeam],
                         'lowerRankedTeam': [lowerRankedTeam],
                         'winner': [higherRankedTeam]}
                    )

                    # concat new record with record of previous games
                    prePlayoffsRecord = pd.concat([prePlayoffsRecord, newPrePlayoffsRecord], ignore_index=True)

                    # break loop
                    break

                # check if lower ranked team in pairing has already won pre playoff round
                elif len(prePlayoffPairingRecord.loc[prePlayoffPairingRecord['winner'] == lowerRankedTeam]) == 2:

                    # create new playoff record for this pairing
                    newPrePlayoffsRecord = pd.DataFrame(
                        {'higherRankedTeam': [higherRankedTeam],
                         'lowerRankedTeam': [lowerRankedTeam],
                         'winner': [lowerRankedTeam]}
                    )

                    # concat new record with record of previous games
                    prePlayoffsRecord = pd.concat([prePlayoffsRecord, newPrePlayoffsRecord], ignore_index=True)

                    # break loop
                    break

                # end of game 1
                game += 1

        # create list of winning teams
        winningTeams = prePlayoffsRecord['winner'].tolist()

        # return winning teams
        return winningTeams

    # if regular playoffs are to be played
    elif playoffsType == 2:

        # create overall playoff round record
        playoffRoundRecord = pd.DataFrame({'higherRankedTeam': [], 'lowerRankedTeam': [], 'winner': []})

        # for each pairing in playoff round
        for pairing in teamPairings:

            # determine higher ranked team
            higherRankedTeam = pairing[0]

            # determine lower ranked team
            lowerRankedTeam = pairing[1]

            # create a within playoff round pairing record of home and away games
            playoffRoundPairingRecord = pd.DataFrame({
                'homeTeam': [i for i in 3 * [higherRankedTeam, lowerRankedTeam] + [higherRankedTeam]],
                'awayTeam': [i for i in 3 * [lowerRankedTeam, higherRankedTeam] + [lowerRankedTeam]],
                'winner': [''] * 7})

            # initialise game count
            game = 1

            # as long as not 8 games have been played
            while game < 8:

                # get index of game
                gameIndex = game - 1

                # define teams in that game
                homeTeam = playoffRoundPairingRecord.loc[gameIndex, 'homeTeam']
                awayTeam = playoffRoundPairingRecord.loc[gameIndex, 'awayTeam']
                skillHomeTeam = skillDictionary[homeTeam]
                skillAwayTeam = skillDictionary[awayTeam]

                # simulate game between teams
                winner = simulate_game(homeTeam, skillHomeTeam, awayTeam, skillAwayTeam,
                                       leagueObject, parameters.playoffs)

                # write winner to record
                playoffRoundPairingRecord.loc[gameIndex, 'winner'] = winner

                # check if higher ranked team in pairing has already won playoff round
                if len(playoffRoundPairingRecord.loc[playoffRoundPairingRecord['winner'] == higherRankedTeam]) == 4:

                    # create new playoff round record for this pairing
                    newPlayoffRoundRecord = pd.DataFrame(
                        {'higherRankedTeam': [higherRankedTeam],
                         'lowerRankedTeam': [lowerRankedTeam],
                         'winner': [higherRankedTeam]}
                    )

                    # concat new record with record of previous games
                    playoffRoundRecord = pd.concat([playoffRoundRecord, newPlayoffRoundRecord], ignore_index=True)

                    # break loop
                    break

                # check if lower ranked team in pairing has already won playoff round
                elif len(playoffRoundPairingRecord.loc[playoffRoundPairingRecord['winner'] == lowerRankedTeam]) == 4:

                    # create new playoff round record for this pairing
                    newPlayoffRoundRecord = pd.DataFrame(
                        {'higherRankedTeam': [higherRankedTeam],
                         'lowerRankedTeam': [lowerRankedTeam],
                         'winner': [lowerRankedTeam]}
                    )

                    # concat new record with record of previous games
                    playoffRoundRecord = pd.concat([playoffRoundRecord, newPlayoffRoundRecord], ignore_index=True)

                    # break loop
                    break

                # end of game 1
                game += 1

        # create list of winning teams
        winningTeams = playoffRoundRecord['winner'].tolist()

        # return winning teams
        return winningTeams


def simulate_playoffs(leagueObject):
    """
    Description:
    Function to simulate pre-playoffs and playoffs

    Input:
    leagueObject (League): The initialised league object of class League

    Returns:
    champion [str]: Name of final champion
    """

    # get required team information
    regularSeasonRanking = leagueObject.regularSeasonRanking

    # pre-playoffs ###

    # extract teams to play pre-playoffs in ranking order
    prePlayoffTeams = regularSeasonRanking.loc[regularSeasonRanking['rank'].isin([7, 8, 9, 10]), 'team'].tolist()

    # extract not pre playoff teams
    notPrePlayoffTeams = regularSeasonRanking.loc[~regularSeasonRanking['rank'].isin([7, 8, 9, 10]), 'team'].tolist()

    # create list of teams in first and second half of ranking so that the teams meet in pre playoffs elementwise
    firstHalf = [prePlayoffTeams[i] for i in range(0, int(len(prePlayoffTeams) / 2))]  # first half of ranking
    secondHalf = [prePlayoffTeams[j] for j in
                  range(-1, -int(len(prePlayoffTeams) / 2) - 1, -1)]  # second half of ranking

    # create pairings
    prePlayoffPairings = list(zip(firstHalf, secondHalf))

    # extract team revenues of pre playoff teams and not pre playoff teams before pre playoff
    prePlayoffTeamRevenuesBefore = leagueObject.get_team_revenues(prePlayoffTeams)
    notPrePlayoffTeamRevenuesBefore = leagueObject.get_team_revenues(notPrePlayoffTeams)

    # simulate pre playoffs
    prePlayoffWinners = simulate_playoff_round(leagueObject, prePlayoffPairings, parameters.prePlayoff)

    # extract team revenues of pre playoff teams and not pre playoff teams before pre playoff
    prePlayoffTeamRevenuesAfter = leagueObject.get_team_revenues(prePlayoffTeams)
    notPrePlayoffTeamRevenuesAfter = leagueObject.get_team_revenues(notPrePlayoffTeams)

    # assertions ###

    # assert that the revenues of pre playoff teams have changed
    assert all([prePlayoffTeamRevenuesBefore[i] != prePlayoffTeamRevenuesAfter[i] for i in
                range(len(prePlayoffTeamRevenuesAfter))])

    # assert that the revenues of non pre playoff teams have not changed
    assert all([notPrePlayoffTeamRevenuesBefore[i] == notPrePlayoffTeamRevenuesAfter[i] for i in
                range(len(notPrePlayoffTeamRevenuesAfter))])

    # playoffs round 1 ###

    # extract top 6 teams after regular season and winning teams of pre playoffs in ranking order
    roundOneTeams = regularSeasonRanking.loc[
        (regularSeasonRanking['rank'].isin([1, 2, 3, 4, 5, 6])) | (
            regularSeasonRanking['team'].isin(prePlayoffWinners)),
        'team'
    ].tolist()

    # extract non round one teams
    notRoundOneTeams = regularSeasonRanking.loc[~regularSeasonRanking['team'].isin(roundOneTeams), 'team'].tolist()

    # create list of teams in first and second half of ranking so that the teams meet in pre playoffs
    firstHalf = [roundOneTeams[i] for i in range(0, int(len(roundOneTeams) / 2))]  # first half of ranking
    secondHalf = [roundOneTeams[j] for j in
                  range(-1, -int(len(roundOneTeams) / 2) - 1, -1)]  # second half of ranking

    # create pairings
    roundOnePairings = list(zip(firstHalf, secondHalf))

    # extract team revenues of round one teams and not round one teams before round one
    roundOneTeamRevenuesBefore = leagueObject.get_team_revenues(roundOneTeams)
    notRoundOneTeamRevenuesBefore = leagueObject.get_team_revenues(notRoundOneTeams)

    # simulate playoffs round 2
    roundOneWinners = simulate_playoff_round(leagueObject, roundOnePairings, parameters.playoffs)

    # extract team revenues of round one teams and not round one teams after round one
    roundOneTeamRevenuesAfter = leagueObject.get_team_revenues(roundOneTeams)
    notRoundOneTeamRevenuesAfter = leagueObject.get_team_revenues(notRoundOneTeams)

    # assertions ###

    # assert that the revenues of round one teams have changed
    assert all([roundOneTeamRevenuesBefore[i] != roundOneTeamRevenuesAfter[i] for i in
                range(len(roundOneTeamRevenuesAfter))])

    # assert that the revenues of non round one teams have not changed
    assert all([notRoundOneTeamRevenuesBefore[i] == notRoundOneTeamRevenuesAfter[i] for i in
                range(len(notRoundOneTeamRevenuesAfter))])

    # playoffs round 2 ###

    # extract round one winners for round two in ranking order
    roundTwoTeams = regularSeasonRanking.loc[regularSeasonRanking['team'].isin(roundOneWinners), 'team'].tolist()

    # extract non round two teams
    notRoundTwoTeams = regularSeasonRanking.loc[~regularSeasonRanking['team'].isin(roundTwoTeams), 'team'].tolist()

    # create list of teams in first and second half of ranking so that the teams meet in playoffs
    firstHalf = [roundTwoTeams[i] for i in range(0, int(len(roundTwoTeams) / 2))]  # first half of ranking
    secondHalf = [roundTwoTeams[j] for j in
                  range(-1, -int(len(roundTwoTeams) / 2) - 1, -1)]  # second half of ranking

    # create pairings
    roundTwoPairings = list(zip(firstHalf, secondHalf))

    # extract team revenues of round two teams and not round two teams before round two
    roundTwoTeamRevenuesBefore = leagueObject.get_team_revenues(roundTwoTeams)
    notRoundTwoTeamRevenuesBefore = leagueObject.get_team_revenues(notRoundTwoTeams)

    # simulate playoffs round 1
    roundTwoWinners = simulate_playoff_round(leagueObject, roundTwoPairings, parameters.playoffs)

    # extract team revenues of round two teams and not round two teams after round two
    roundTwoTeamRevenuesAfter = leagueObject.get_team_revenues(roundTwoTeams)
    notRoundTwoTeamRevenuesAfter = leagueObject.get_team_revenues(notRoundTwoTeams)

    # assertions ###

    # assert that the revenues of round two teams have changed
    assert all([roundTwoTeamRevenuesBefore[i] != roundTwoTeamRevenuesAfter[i] for i in
                range(len(roundTwoTeamRevenuesAfter))])

    # assert that the revenues of non round two teams have not changed
    assert all([notRoundTwoTeamRevenuesBefore[i] == notRoundTwoTeamRevenuesAfter[i] for i in
                range(len(notRoundTwoTeamRevenuesAfter))])

    # playoffs round 3 ###

    # extract round two winners for round three in ranking order
    roundThreeTeams = regularSeasonRanking.loc[regularSeasonRanking['team'].isin(roundTwoWinners), 'team'].tolist()

    # extract non round three teams
    notRoundThreeTeams = regularSeasonRanking.loc[~regularSeasonRanking['team'].isin(roundThreeTeams), 'team'].tolist()

    # create pairing
    roundThreePairing = [(roundThreeTeams[0], roundThreeTeams[1])]

    # extract team revenues of round three teams and not round three teams before round three
    roundThreeTeamRevenuesBefore = leagueObject.get_team_revenues(roundThreeTeams)
    notRoundThreeTeamRevenuesBefore = leagueObject.get_team_revenues(notRoundThreeTeams)

    # simulate playoffs round 3
    champion = simulate_playoff_round(leagueObject, roundThreePairing, parameters.playoffs)

    # extract team revenues of round three teams and not round three teams after round three
    roundThreeTeamRevenuesAfter = leagueObject.get_team_revenues(roundThreeTeams)
    notRoundThreeTeamRevenuesAfter = leagueObject.get_team_revenues(notRoundThreeTeams)

    # assertions ###

    # assert that the revenues of round three teams have changed
    assert all([roundThreeTeamRevenuesBefore[i] != roundThreeTeamRevenuesAfter[i] for i in
                range(len(roundThreeTeamRevenuesAfter))])

    # assert that the revenues of non round three teams have not changed
    assert all([notRoundThreeTeamRevenuesBefore[i] == notRoundThreeTeamRevenuesAfter[i] for i in
                range(len(notRoundThreeTeamRevenuesAfter))])

    # return champion
    return champion[0]
