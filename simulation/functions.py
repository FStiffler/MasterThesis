from parameters import *
import numpy as np
import pandas as pd
import pulp as pl
import random as ra
from pulp import PULP_CBC_CMD


def skill_maximization(playerPool, teamBudget):
    """
    Description:
    Function which allows team to select players while maximizing skill given a team size and budget constraint

    Input:
    playerPool (PlayerPool): A player pool of object PlayerPool
    teamBudget (dbl): The budget constraint for a particular team used to optimize skill

    Returns:
    selectedPlayers (pandas dataframe): A pandas dataframe which includes data about selected players
    """

    # initialize variables
    playerData = playerPool.get_all_player_data()  # get data from all players as data frame
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
    prob += pl.lpSum(binaries[i] for i in range(len(players))) == teamSize  # team size constraint
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
        playerData['ID'].isin(  # filter ID's in array
            np.array(
                solutionDF.Variable.str.split('_').tolist()  # extract player ID from variable name
            )[:, 1].astype(int)  # select column with ID and define them as integer
        )
    ]

    # assert that constraints hold since the solver does not throw an error when not converging to a solution
    assert len(selectedPlayers) == teamSize
    assert selectedPlayers.Salary.sum() <= teamBudget

    # return selected team
    return selectedPlayers


def identify_conflicts(optimalPlayers, optimalPlayersSet):
    """
    Description:
    Function to identify players who multiple teams are interested in

    Input:
    optimalPlayers (dict): A dictionary which shows the players selected by every team after the maximization process
    derived from an object with class League after calling method select_optimal_players
    optimalPlayersSet (set): A set which shows all unique players selected by any team during the maximization process
    derived from an object with class League after calling method select_optimal_players

    Returns:
    conflicts (dict): A dictionary showing the conflicting player id as key and all interested teams as values in a list
    noConflicts (dict): A dictionary showing the non-conflicting player id as key and the interested team as value in a list
    """

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

            # add player id as key and list of interested teams as value to the conflicts dictionary
            conflicts[player] = interestedTeams.team.tolist()

        # if only one team wants to acquire a player
        else:

            # add player id as key and list containing interested team as value to the non conflicts dictionary
            noConflicts[player] = interestedTeams.team.tolist()

    # return dictionaries
    return conflicts, noConflicts


def shuffle_conflicts(conflicts):
    """
    Description:
    Function to shuffle order of conflicts to be solved

    Input:
    finalPlayerSelection (dict): A dictionary which contains all players and according interested teams

    Returns:
    shuffledConflicts (dict): The same dictionary as input but now with shuffled conflicts
    """

    # create list of conflict items where each item consists of a tuple with the conflicting player and a list of teams
    conflictItems = list(conflicts.items())

    # shuffle the tuples
    ra.shuffle(conflictItems)

    # create a shuffled dictionary
    shuffledConflicts = dict(conflictItems)

    # return
    return shuffledConflicts


def assign_player(finalPlayerSelection, player, team):
    """
    Description:
    Function to assign a player to a specific team

    Input:
    finalPlayerSelection (dict): A dictionary which shows the final player selection of teams so far
    derived from an object with class League
    player (int): The new player to be added to the already existing selection of players
    team (str): The team to which the new player is to be assigned

    Returns:
    finalPlayerSelection (dict): Updates and returns final player selection
    """

    # append the new player to a list of existing players for a team
    finalPlayerSelection[team].append(player)

    # return
    return finalPlayerSelection


def update_team_payroll(finalPlayerSelection, teamData, allPlayersData):
    """
    Description:
    Function to update the team payrolls of all teams

    Input:
    finalPlayerSelection (dict): A dictionary which shows the final player selection of teams so far
    derived from an object with class League
    teamData (dataframe): A dataframe which contains information about the team and is initialised when a object of class League is created
    allPlayersData (dataframe): A dataframe with information about all players in the player pool created when player pool was initialised

    Returns:
    teamData (dict): Updates and returns information about the teams
    """

    # obtain salary for every selected player
    salaryDict = {team: allPlayersData.loc[allPlayersData['ID'].isin(players), 'Salary'].values.tolist() for
                  (team, players) in finalPlayerSelection.items()}

    # calculate sum of salaries
    salarySumDict = {team: sum(salaries) for (team, salaries) in salaryDict.items()}

    # create list of salary sums and append to payroll information about teamData
    teamData['payroll'] = list(salarySumDict.values())

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


def teams_choose_replacement(player, team, allPlayersData, availablePlayersData, teamData):
    """
    Description:
    Function representing the replacement decision by teams which were not picked a player they considered optimal

    Input:
    player (int): The player which did not join the team and thus needs to be replaced
    team (str): The team which has to decide which player to choose now
    allPlayersData (dataframe): Contains information about all players in the player pool
    remainingPlayersData (dataframe): Contains all data about the remaining players in the player pool
    teamData (team): A dataframe which contains team information

    Returns:
    replacementPlayer (int): Id of replacement player
    """

    # filter player skill from player to be replaced
    playerSkill = allPlayersData.loc[allPlayersData['ID'] == player, 'Skill'].values[0]

    # add new column with absolut skill gab to data about still available players
    availablePlayersData['Skill Gab'] = abs(playerSkill - availablePlayersData.Skill)

    # order available player data according to skill gab
    availablePlayersData.sort_values('Skill Gab', inplace=True)

    # identify current team payroll
    teamPayroll = teamData.loc[teamData['team'] == team, 'payroll'].values[0]

    # identify team budget
    teamBudget = teamData.loc[teamData['team'] == team, 'budget'].values[0]

    # initialise index for loop
    index = 0

    # while index is smaller then length of dataframe containing replacement players
    while index < len(availablePlayersData):

        # identify a replacement player in increasing order of skill gab
        replacementPlayerInfo = availablePlayersData.iloc[index, ]

        # identify salary of replacement player
        replacementPlayerSalary = replacementPlayerInfo['Salary']

        # if addition of player salary to team payroll would lead to a violation of team budget
        if teamPayroll + replacementPlayerSalary > teamBudget:

            # increase index by one to try next player in order
            index += 1

            # raise exception if there is no other player left and the budget constraint is violated
            if index == len(availablePlayersData):
                raise Exception('No replacement player left but breach of budget constraint')

        # if there is no violation
        else:

            # identify replacement player by ID
            replacementPlayer = int(replacementPlayerInfo['ID'])

            # break loop
            break

    # return id of chosen player
    return replacementPlayer

def no_duplicates(finalPlayerSelection):
    """
    Description:
    Function to check if any player appears twice in the final teams

    Input:
    finalPlayerSelection (dict): dictionary showing final selection of teams

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