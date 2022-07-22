import parameters
import functions
import pandas as pd
import random as ra
import numpy as np


# define player pool as class
class PlayerPool(object):
    def __init__(self, season=1, maximalBudget=max(parameters.initialTeamBudget), allowedImports=4):
        """
        Description:
        Initializes the player pool object. The object is fully initialised based on parameters and variables

        Input:
        season (int): the index of season currently played, default is 1
        maximalBudget: the highest team budget, default is defined highest initial team budget

        A player pool object has the following attributes:
        self.size (int): Determines pool size (number of available players)
        self.allPlayersData (dataframe): A dataframe with information about all initialised players, infos are to be found in parameter file
        self.availablePlayersData (dataframe): A dataframe with information about available players not yet picked by a team, initialised with all players
        """
        self.maximalSalary = round(parameters.bestPlayerRevenueShare * maximalBudget)  # maximal salary for best available player, references 'w_max' in thesis
        self.size = round(parameters.initialSwissPlayers * (1 + parameters.naturalPlayerBaseGrowth) ** season + allowedImports * parameters.leagueSize)  # new player pool size, references 'k_t' in thesis
        self.allPlayers = np.arange(start=1, stop=self.size + 1)  # create players with numbers from 1 to player pool size to create all players in player pool, references 'p' in thesis
        self.allPlayerSkills = np.round(np.random.beta(a=parameters.alpha, b=parameters.beta, size=self.size), 2)  # draw skill from beta distribution to create all skill levels of players in player pool, references 'S_p' in thesis
        self.allPlayerSalaries = np.round(self.maximalSalary * self.allPlayerSkills * functions.supply_effect(self.size))  # calculate player salaries to create all salaries in the player pool, references 'W_p' in thesis
        self.allPlayersData = self.get_all_player_data()
        self.availablePlayersData = self.get_all_player_data()

    def get_all_player_data(self):
        """
        Description:
        Create data frame with all player information

        Returns:
        allPlayersData (dataframe): Dataframe with information about all players
        """
        allPlayersData = pd.DataFrame(
            data=np.column_stack((self.allPlayers, self.allPlayerSkills, self.allPlayerSalaries)),
            # arrays as columns
            columns=["player", "skill", "salary"]
        )
        allPlayersData = allPlayersData.astype({"player": int, 'salary': int})  # change player to integer

        return allPlayersData

    def get_all_players(self):
        """
        Description:
        Get all players as list

        Returns:
        allPlayersList (list): List of all players
        """
        allPlayersList = self.allPlayersData['player'].tolist()

        return allPlayersList

    def get_all_player_skills(self):
        """
        Description:
        Get skill levels of all players as list

        Returns:
        allPlayerSkillsList (list) : List of skill levels of all players
        """
        allPlayerSkillsList = self.allPlayersData['skill'].tolist()

        return allPlayerSkillsList

    def get_all_player_salaries(self):
        """
        Description:
        Get all player salaries as a list

        Returns:
        allPlayerSalariesList (list): List of salaries of all players
        """
        allPlayerSalariesList = self.allPlayersData['salary'].tolist()

        return allPlayerSalariesList

    def get_available_players_set(self):
        """
        Description:
        Get set of all available players

        Returns:
        availablePlayersSet (list): Set of all available players
        """
        availablePlayersSet = set(self.availablePlayersData['player'].tolist())

        return availablePlayersSet

    def update_player_pool_after_maximization(self, optimalPlayersSet):
        """
        Description:
        Update the players in the player pool after teams have selected optimal players in maximization process

        Input:
        optimalPlayersSet (set): the set of optimal players chosen by all teams derived from an object with class League
        after calling the class method select_optimal_players

        Update:
        self.availablePlayersData (dataframe): Dataframe of available players after optimal players are removed from from the dataframe
        """

        # convert set to a list
        optimalPlayersList = list(optimalPlayersSet)

        # remove optimal players from available player data
        self.availablePlayersData = self.availablePlayersData.loc[
            ~self.availablePlayersData['player'].isin(optimalPlayersList)]

        # create set of available players
        availablePlayersSet = self.get_available_players_set()

        # assert that there is no intersection between the still available and the selected players
        assert len(availablePlayersSet.intersection(optimalPlayersSet)) == 0

    def remove_player_from_available(self, player):
        """
        Description:
        Remove a single player selected by a team as replacement from the pool of available players

        Input:
        player (int): The selected player to be removed from the available players

        Update:
        self.availablePlayersData (dataframe): Dataframe of available players after replacement player was removed
        """

        # remove optimal players from available player data
        self.availablePlayersData = self.availablePlayersData.loc[self.availablePlayersData['player'] != player]

    def get_player_stats(self):
        """
        Description:
        Calculate and return player stats

        Return:
        seasonPlayerResults (data frame): Data frame with player stats, one metric per column
        """

        seasonPlayerResults = pd.DataFrame({
            'players': [len(self.allPlayers)],
            'lowestSalary': [np.round(self.allPlayerSalaries.min())],
            'averageSalary': [np.round(np.mean(self.allPlayerSalaries))],
            'medianSalary': [np.round(np.median(self.allPlayerSalaries))],
            'maximalSalary': [np.round(self.allPlayerSalaries.max())]
        })

        return seasonPlayerResults



# define league as class
class League(object):
    def __init__(self):
        """
        Description:
        Initializes a league object. The object is fully initialised based on parameters and variables

        A league object has the following attributes:
        self.teamData (dataframe): Dataframe with information about the team, parameter description in parameters file
        self.optimalPlayers (dict): Dictionary with each team as key and a list of optimal players selected by the team in maximization process, is initialised empty
        self.optimalPlayersSet (set): Set containing every selected player in the maximization process once, is initialised empty
        self.optimalPlayersData (dataframe): Dataframe containing information about the selected players in maximization process, is initialised empty
        self.finalPlayerSelection (dict): Dictionary with each team as key and a list of the final players selected by the team in replacement process, is initialised empty
        self.regularSeasonRanking (dataframe): Dataframe which contains regular season ranking, is initialised empty
        """
        self.teamData = pd.DataFrame({'team': parameters.teams,
                                      'budget': parameters.initialTeamBudget,  # create variable team budgets, references 'R_tot_it-1',
                                      'payroll': [0] * parameters.leagueSize,  # create variable team payrolls, references 'sum(W_p * d_p)' in thesis
                                      'totalSkill': [0] * parameters.leagueSize,  # create variable team skills, references 'S_i' in thesis
                                      'revenue': [0] * parameters.leagueSize,  # create variable revenue, references 'R_tot_it' in thesis
                                      'wins': [0] * parameters.leagueSize,  # create variable for win count
                                      'games': [0] * parameters.leagueSize,  # create variable for game count
                                      'rank': [0] * parameters.leagueSize,  # create variable for final regular season rank
                                      'eliminatedRS': [0] * parameters.leagueSize,  # create binary variable indicating regular season elimination
                                      'eliminatedPP': [0] * parameters.leagueSize,  # create binary variable indicating pre playoffs elimination
                                      'eliminatedPR1': [0] * parameters.leagueSize,  # create binary variable indicating playoffs round 1 elimination
                                      'eliminatedPR2': [0] * parameters.leagueSize,  # create binary variable indicating playoffs round 2 elimination
                                      'eliminatedPR3': [0] * parameters.leagueSize,  # create binary variable indicating playoffs round 3 elimination
                                      'champion': [0] * parameters.leagueSize,  # create binary variable indicating league champion
                                      'monetaryFactor': parameters.monetaryFactor,
                                      'marketSize': parameters.marketSize,
                                      'seasonPhaseFactor': parameters.seasonPhaseFactor,
                                      'compBalanceEffect': parameters.compBalanceEffect})
        self.optimalPlayers = {}
        self.optimalPlayersSet = set()
        self.optimalPlayersData = pd.DataFrame()
        self.finalPlayerSelection = {}
        self.regularSeasonRanking = pd.DataFrame()

    def get_teams(self):
        """
        Description:
        Get all teams as list

        Returns:
        teamsList (list): List of all teams
        """
        teamsList = self.teamData['team'].tolist()

        return teamsList

    def get_team_budgets(self):
        """
        Description:
        Get all team budgets

        Returns:
        teamBudgetsList (list): List of all team budgets
        """
        teamBudgetsList = self.teamData['budget'].tolist()

        return teamBudgetsList

    def get_team_skills(self):
        """
        Description:
        Get aggregated skill levels of all teams

        Returns:
        teamSkillsList (list): List with aggregated skill level of every team
        """
        teamSkillsList = self.teamData['totalSkill'].tolist()

        return teamSkillsList

    def get_team_revenues(self, teams=None):
        """
        Description:
        Get a list of all team revenues

        Input:
        teams (list): The teams from which the revenues are required, default is none in which case all revenues are returned

        Returns:
        teamRevenues (list): List with all team revenues
        """
        # if no teams specific teams are asked
        if teams is None:

            # return all revenues
            teamRevenuesList = self.teamData['revenue'].tolist()

        elif type(teams) is list:

            # return all revenues of requested teams
            teamRevenuesList = self.teamData.loc[self.teamData['team'].isin(teams), 'revenue'].tolist()

        return teamRevenuesList

    def get_skill_dictionary(self):
        """
        Description:
        Get a dictionary of teams and their according skill levels

        Returns:
        skillDictionary (dict): Dictionary with team as key and team skill as value
        """
        # get required team information
        teams = self.get_teams()
        skills = self.get_team_skills()

        # create skill dictionary
        skillDictionary = {teams[team]: round(skills[team], 2) for team in range(len(teams))}

        return skillDictionary

    def update_team_data_post_regular_season(self):
        """
        Description:
        update team data with regular season results

        updates:
        self.teamData (data frame): Data frame with data to team performance in season
        """
        # get required team information
        teams = self.get_teams()
        teamData = self.teamData.copy()
        regularSeasonRanking = self.regularSeasonRanking.copy()

        # for each team
        for team in teams:
            # update team data
            teamData.loc[teamData['team'] == team, 'wins'] = regularSeasonRanking.loc[regularSeasonRanking['team'] == team, 'wins'].values[0]
            teamData.loc[teamData['team'] == team, 'games'] = regularSeasonRanking.loc[regularSeasonRanking['team'] == team, 'games'].values[0]
            teamData.loc[teamData['team'] == team, 'rank'] = regularSeasonRanking.loc[regularSeasonRanking['team'] == team, 'rank'].values[0]

        # label eliminated teams in regular season
        teamData['eliminatedRS'] = teamData['rank'].map(lambda x: 1 if x in [11, 12, 13, 14] else 0)

        # assign new data back
        self.teamData = teamData

    def check_intersection_optimal_final(self):
        """
        Description:
        Check how many players initially wanted by the team end up on the team

        Output:
        Printing intersection for each team
        """
        # for each team
        for team in self.finalPlayerSelection:
            # extract final selection as set
            finalSelectionSet = set(self.finalPlayerSelection[team])

            # extract optimal selection as set
            optimalSelectionSet = set(self.optimalPlayers[team])

            # create intersection
            intersection = finalSelectionSet.intersection(optimalSelectionSet)

            # print
            print('Team: {}, Total: {}, Set: {}'.format(team, len(intersection), intersection))

    def select_optimal_players(self, playerPool):
        """
        Description:
        Let each team solve the maximization problem of player selection

        Input:
        playerPool (PlayerPool): The initialised player pool of object PlayerPool

        Updates:
        self.optimalPlayers (dict): updates the dictionary with the selected optimal players by each team
        self.optimalPlayersSet (set): updates the set with all unique players selected over all teams
        self.optimalPlayersData (set): updates the dataframe with the information about the optimal players
        """

        # initialise new empty dictionary for player selection
        optimalPlayers = {}

        # get required team information
        teams = self.get_teams()
        teamBudgets = self.get_team_budgets()

        # for each team in the league
        for team in range(len(teams)):
            # select optimal players based on skill maximization
            selectedPlayers = functions.skill_maximization(playerPool, teamBudgets[team])

            # add team as key and the list of selected players as value do the dictionary
            optimalPlayers[teams[team]] = selectedPlayers.player.tolist()

        # overwrite old dictionary with new dictionary
        self.optimalPlayers = optimalPlayers

        # create set of optimal players selected by all teams based on dictionary
        optimalPlayersSet = set().union(*list(self.optimalPlayers.values()))

        # overwrite old set with new set, each selected player appears exactly once
        self.optimalPlayersSet = optimalPlayersSet

        # import data of all players
        allPlayersData = playerPool.allPlayersData

        # extract data from selected players and assign it
        self.optimalPlayersData = allPlayersData.loc[allPlayersData['player'].isin(self.optimalPlayersSet)]

    def resolve_player_conflicts(self, playerPool):
        """
        Description:
        Assign players which are only picked by one team to that team,
        Resolve conflicts in case players are selected by multiple teams by applying a decision rule which let's
        the player pick a team and let the other teams which were not picked by the players, immediately pick an
        a similarly skilled replacement player

        Input:
        playerPool (PlayerPool): An object of class PlayerPool

        Updates:
        playerPool (PlayerPool): The selected replacement players are removed from available players in player pool
        self.finalPlayerSelection (dict): The dictionary with the final player selection is completed
        self.teamData (dataframe): The dataframe with information about the teams is completed
        """
        # get required team information
        teams = self.get_teams()

        # identify conflicts and non conflicts
        conflicts, noConflicts = functions.identify_conflicts(self)

        # shuffle conflicts
        shuffledConflicts = functions.shuffle_conflicts(conflicts)

        # initialise dictionary for final player selection by adding a key for each team and empty lists as values
        self.finalPlayerSelection = {team: [] for team in teams}

        # for each player without conflict
        for player in noConflicts:
            # define the team which has selected the player
            team = noConflicts[player][0]

            # assign the player to the according team
            self.finalPlayerSelection = functions.assign_player(self, player, team)

        # update data for all teams
        self.teamData = functions.update_team_info(self, playerPool.allPlayersData)

        # for each player with conflict
        for player in shuffledConflicts:
            # define the potential teams a player can choose
            interestedTeams = shuffledConflicts[player]

            # let the player decide which team to join
            chosenTeam = functions.player_chooses_team(interestedTeams)

            # assign the player to the team he decided to join
            self.finalPlayerSelection = functions.assign_player(self, player, chosenTeam)

            # remove chosen team from list of interested teams and from dictionary with shuffled conflicts
            interestedTeams.remove(chosenTeam)

            # shuffle the remaining teams so that teams can pick a replacement in a random order
            ra.shuffle(interestedTeams)

        # update team data after all players have chosen their team
        self.teamData = functions.update_team_info(self, playerPool.allPlayersData)

        # for every player which now needs to be replaced by the remaining teams in each conflict
        for player in shuffledConflicts:

            # extract the remaining teams in same conflict order as players have chosen teams
            remainingTeams = shuffledConflicts[player]

            # for each remaining team among the remaining teams in one conflict
            for remainingTeam in remainingTeams:
                # a replacement player for initial player is defined
                replacementPlayer = functions.teams_choose_replacement(player, remainingTeam, playerPool, self)

                # add replacement player to the remaining team which has selected the player
                self.finalPlayerSelection = functions.assign_player(self, replacementPlayer, remainingTeam)

                # remove replacement player from available players in player pool
                playerPool.remove_player_from_available(replacementPlayer)

            # update team data after each conflict so that it is up to date when resolving next conflict
            self.teamData = functions.update_team_info(self, playerPool.allPlayersData)

        # assert that constraints also hold in final player selection
        assert all(list({team: len(players) == parameters.teamSize for (team, players) in
                         self.finalPlayerSelection.items()}.values()))  # all teams have the defined number of players
        assert all([True if self.teamData.loc[x, 'budget'] - self.teamData.loc[x, 'payroll'] > 0 else False for x in
                    range(len(self.teamData))])  # payroll below budget
        assert functions.no_duplicates(self.finalPlayerSelection)

    def calculate_game_revenue(self, homeTeam, winPercentageHome, seasonPhase):
        """
        Description:
        Calculates the revenue of the home team in one single game and appends it to the revenue information of the
        team

        Input:
        homeTeam (str): Name of home team for which game revenue is to be calculated
        winPercentageHome (float): The winning percentage of the home team winning
        seasonPhase (int): Integer defining in which phase of season we are, 0 = Regular Season, 1 or 2 = pre playoffs
        and playoffs respectively

        Update:
        self.teamData (dataframe): The dataframe containing team information is updated with new revenue data
        """

        # extract home team information in order to calculate game revenues ###

        # if it is a game in the regular season
        if seasonPhase == 0:

            # extract regular season factor
            seasonPhaseFactor = self.teamData.loc[self.teamData['team'] == homeTeam, 'seasonPhaseFactor'].values[0][0]

        # if it is a game in the playoffs
        elif seasonPhase in [1, 2]:

            # extract playoff factor
            seasonPhaseFactor = self.teamData.loc[self.teamData['team'] == homeTeam, 'seasonPhaseFactor'].values[0][1]

        # extract monetaryFactor
        monetaryFactor = self.teamData.loc[self.teamData['team'] == homeTeam, 'monetaryFactor'].values[0]

        # extract market size
        marketSize = self.teamData.loc[self.teamData['team'] == homeTeam, 'marketSize'].values[0]

        # extract effect of competitive balance
        compBalanceEffect = self.teamData.loc[self.teamData['team'] == homeTeam, 'compBalanceEffect'].values[0]

        # calculate game revenue for team
        gameRevenue = monetaryFactor * seasonPhaseFactor * (
                marketSize * winPercentageHome - (compBalanceEffect / 2) * winPercentageHome ** 2)

        # update revenue of home team
        self.teamData.loc[self.teamData['team'] == homeTeam, 'revenue'] += gameRevenue

    def simulate_season(self):
        """
        Description:
        Simulate a whole season where each team plays against every other team four times during a regular season.
        After that, pre-playoffs and playoffs follow. One champion is determined.

        Output:
        The name of the champion is printed out
        """
        # simulate regular season to obtain ranking
        self.regularSeasonRanking = functions.simulate_regular_season(self)

        # update team data based on regular season ranking
        self.update_team_data_post_regular_season()

        # simulate playoffs
        champion = functions.simulate_playoffs(self)

        print(champion)

    def calculate_season_revenue(self, season):
        """
        Description:
        Calculates the total season revenue of all teams

        Input:
        season (int): Index of current season

        Update:
        self.teamData (dataframe): The dataframe containing team information is updated with final revenue data
        """
        # add remaining budget to revenue
        self.teamData['revenue'] += self.teamData['budget'] - self.teamData['payroll']

        # calculate broadcasting revenue for this season
        currentBroadcastingRevenue = parameters.initialBroadcastingRevenue * (
                1 + parameters.broadcastingRevenueGrowth) ** season

        # add broadcasting revenue to revenue
        self.teamData['revenue'] += currentBroadcastingRevenue

        # round values
        self.teamData['revenue'] = self.teamData['revenue'].round().astype(int)

    def reset_for_new_season(self):
        """
        Description:
        Resets the league object for a new season simulation

        Update:
        self.teamData (dataframe): team data is prepared for new season
        self.optimalPlayers (dict): reset to state of league initialisation
        self.optimalPlayersSet (set): reset to state of league initialisation
        self.optimalPlayersData (dataframe): reset to state of league initialisation
        self.finalPlayerSelection (dict): reset to state of league initialisation
        self.regularSeasonRanking (dataframe): reset to state of league initialisation
        """
        # extract new team budgets which is revenue of previous season
        budgets = self.teamData['revenue'].tolist()

        # update teamData
        self.teamData = pd.DataFrame({'team': parameters.teams,
                                      'budget': budgets,
                                      'payroll': [0] * parameters.leagueSize,  # create variable team payrolls, references 'sum(W_p * d_p)' in thesis
                                      'totalSkill': [0] * parameters.leagueSize,  # create variable team skills, references 'S_i' in thesis
                                      'revenue': [0] * parameters.leagueSize,  # create variable revenue, references 'R_tot_it' in thesis
                                      'wins': [0] * parameters.leagueSize,  # create variable for win count
                                      'games': [0] * parameters.leagueSize,  # create variable for game count
                                      'rank': [0] * parameters.leagueSize,  # create variable for final regular season rank
                                      'eliminatedRS': [0] * parameters.leagueSize,  # create binary variable indicating regular season elimination
                                      'eliminatedPP': [0] * parameters.leagueSize,  # create binary variable indicating pre playoffs elimination
                                      'eliminatedPR1': [0] * parameters.leagueSize,  # create binary variable indicating playoffs round 1 elimination
                                      'eliminatedPR2': [0] * parameters.leagueSize,  # create binary variable indicating playoffs round 2 elimination
                                      'eliminatedPR3': [0] * parameters.leagueSize,  # create binary variable indicating playoffs round 3 elimination
                                      'champion': [0] * parameters.leagueSize,  # create binary variable indicating league champion
                                      'monetaryFactor': parameters.monetaryFactor,
                                      'marketSize': parameters.marketSize,
                                      'seasonPhaseFactor': parameters.seasonPhaseFactor,
                                      'compBalanceEffect': parameters.compBalanceEffect})
        self.optimalPlayers = {}
        self.optimalPlayersSet = set()
        self.optimalPlayersData = pd.DataFrame()
        self.finalPlayerSelection = {}
        self.regularSeasonRanking = pd.DataFrame()


