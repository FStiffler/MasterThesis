import parameters
import functions
import pandas as pd
import random as ra
import numpy as np


# define domestic player pool as class
class DomesticPlayerPool(object):
    def __init__(self, season=1, maximalBudget=max(parameters.initialTeamBudget), allowedImports=4):
        """
        Description:
        Initializes the domestic player pool object. The object is fully initialised based on parameters and variables

        Input:
        season (int): the index of season currently played, default is 1
        maximalBudget (int): the highest team budget, default is defined highest initial team budget
        allowedImports (int): the number of allowed import players per team in the league, default is 4

        A domestic player pool object has the following attributes:
        self.domesticTeamSize (int): determines the number of domestic players on team
        self.domesticSize (int): determines pool size of domestic player pool (number of available players)
        self.totalSize (int): determines the total size of player pool faced by teams
        self.allPlayers (list): list with player ids of the form d_id
        self.allPlayerSkills (array): array with all player skills
        self.allPlayerSkills (array): array with all player skills
        self.allPlayersData (dataframe): A dataframe with information about all initialised players, infos are to be found in parameter file
        self.availablePlayersData (dataframe): A dataframe with information about available players not yet picked by a team, initialised with all players
        """
        self.domesticTeamSize = parameters.teamSizeMax - allowedImports  # domestic players of team, references 'h_domestic' in thesis
        self.domesticSize = round(parameters.initialSwissPlayers * (1 + parameters.naturalPlayerBaseGrowth) ** season)  # domestic player pool size, references 'k_domestic' in thesis
        self.totalSize = self.domesticSize + allowedImports  # total player pool size faced by teams, references 'k_t' in thesis
        self.maximalSalary = round(parameters.bestPlayerRevenueShare * maximalBudget)  # maximal salary for best available player, references 'w_max' in thesis
        self.allPlayers = ['d'+str(p) for p in range(1, self.domesticSize+1)]  # create players with numbers from 1 to domestic player pool size to create all players in player pool, references 'p_domestic' in thesis
        self.allPlayerSkills = np.round(np.random.beta(a=parameters.alpha, b=parameters.beta, size=self.domesticSize), 2)  # draw skill from beta distribution to create all skill levels of players in player pool, references 'S_p' in thesis
        self.allPlayerSalaries = np.round(self.maximalSalary * self.allPlayerSkills * functions.supply_effect(self.totalSize))  # calculate player salaries to create all salaries in the player pool, references 'W_p' in thesis
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
            {
                "player": self.allPlayers,
                "skill": self.allPlayerSkills.tolist(),
                "salary": self.allPlayerSalaries.tolist()
            }
        )
        allPlayersData = allPlayersData.astype({"player": str, "salary": int})  # change player to integer

        return allPlayersData

    def get_domestic_team_size(self):
        """
        Description:
        Get the number of required domestic players per team

        Returns:
        domesticTeamSize (int): Number of domestic players
        """

        return self.domesticTeamSize

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

    def update_player_pool_after_maximization(self, optimalDomesticPlayersSet):
        """
        Description:
        Update the players in the player pool after teams have selected optimal players in maximization process

        Input:
        optimalDomesticPlayersSet (set): the set of optimal domestic players chosen by all teams derived from an object with class League
        after calling the class method select_optimal_players

        Update:
        self.availablePlayersData (dataframe): Dataframe of available players after optimal players are removed from from the dataframe
        """

        # convert set to a list
        optimalDomesticPlayersList = list(optimalDomesticPlayersSet)

        # remove optimal players from available player data
        self.availablePlayersData = self.availablePlayersData.loc[
            ~self.availablePlayersData['player'].isin(optimalDomesticPlayersList)]

        # create set of available players
        availablePlayersSet = self.get_available_players_set()

        # assert that there is no intersection between the still available and the selected players
        assert len(availablePlayersSet.intersection(optimalDomesticPlayersSet)) == 0

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


# define foreign player pool as class
class ForeignPlayerPool(object):
    def __init__(self, season=1, maximalBudget=max(parameters.initialTeamBudget), allowedImports=4):
        """
        Description:
        Initializes the foreign player pool object. The object is fully initialised based on parameters and variables

        Input:
        season (int): the index of season currently played, default is 1
        maximalBudget (int): the highest team budget, default is defined highest initial team budget
        allowedImports (int): the number of allowed import players per team in the league, default is 4

        A foreign player pool object has the following attributes:
        self.domesticSize (int): determines pool size of domestic player pool (number of available players)
        self.totalSize (int): determines the total size of player pool faced by a team
        self.allPlayers (list): list with player ids of the form f_id
        self.allPlayerSkills (array): array with all player skills
        self.allPlayerSkills (array): array with all player skills
        self.allPlayersData (dataframe): A dataframe with information about all initialised players, infos are to be found in parameter file
        self.availablePlayersData (dataframe): A dataframe with information about available players not yet picked by a team, initialised with all players
        """
        self.domesticSize = round(parameters.initialSwissPlayers * (1 + parameters.naturalPlayerBaseGrowth) ** season)  # domestic player pool size, references 'k_domestic' in thesis
        self.totalSize = self.domesticSize + allowedImports  # total player pool size faced by teams, references 'k_t' in thesis
        self.maximalSalary = round(parameters.bestPlayerRevenueShare * maximalBudget)  # maximal salary for best available player, references 'w_max' in thesis
        self.allPlayers = ['f'+str(p) for p in range(1, allowedImports * 100+1)]  # create players with numbers from 1 to size of foreign player pool which is infinity but is approximated by the number of possible player skills multiplied by the number of allowed imports , references 'p_foreign' in thesis
        self.allPlayerSkills = np.round(np.repeat(np.arange(start=0.01, stop=1.01, step=0.01), allowedImports), 2)  # create all possible skill levels from 0 to 1 repeated as many times as there are allowed imports, references 'S_p' in thesis
        self.allPlayerSalaries = np.round(self.maximalSalary * self.allPlayerSkills * functions.supply_effect(self.totalSize))  # calculate player salaries to create all salaries in the player pool, references 'W_p' in thesis
        self.allPlayersData = self.get_all_player_data()

    def get_all_player_data(self):
        """
        Description:
        Create data frame with all player information

        Returns:
        allPlayersData (dataframe): Dataframe with information about all players
        """
        allPlayersData = pd.DataFrame(
            {
                "player": self.allPlayers,
                "skill": self.allPlayerSkills.tolist(),
                "salary": self.allPlayerSalaries.tolist()
            }
        )
        allPlayersData = allPlayersData.astype({"player": str, "salary": int})  # change player to integer

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


# define league as class
class League(object):
    def __init__(self):
        """
        Description:
        Initializes a league object. The object is fully initialised based on parameters and variables

        A league object has the following attributes:
        self.teamData (dataframe): Dataframe with information about the team, parameter description in parameters file
        self.optimalDomesticPlayers (dict): Dictionary with each team as key and a list of optimal domestic players selected by the team in maximization process, is initialised empty
        self.optimalDomesticPlayersSet (set): Set containing every selected domestic player in the maximization process once, is initialised empty
        self.optimalDomesticPlayersData (dataframe): Dataframe containing information about the selected domestic players in maximization process, is initialised empty
        self.optimalDomesticPlayers (dict): Dictionary with each team as key and a list of optimal import players selected by the team in maximization process, is initialised empty
        self.finalPlayerSelection (dict): Dictionary with each team as key and a list of the final players selected by the team in replacement process, is initialised empty
        self.regularSeasonRanking (dataframe): Dataframe which contains regular season ranking, is initialised empty
        self.leagueCondition (str): String inidicating if a simulation breaking condition occures, is initialised with None
        """
        self.teamData = pd.DataFrame({'team': parameters.teams,
                                      'domestics': [0] * parameters.leagueSize,  # the number of domestic players
                                      'imports': [0] * parameters.leagueSize,  # the number of import players
                                      'budget': parameters.initialTeamBudget,  # create variable team budgets, references 'R_tot_it-1',
                                      'salaryCap': [False] * parameters.leagueSize,  # create variable salary cap, references 'R_cap'
                                      'effectiveBudget': [0] * parameters.leagueSize,  # create variable for the budget teams can actually spend
                                      'payroll': [0] * parameters.leagueSize,  # create variable team payrolls, references 'sum(W_p * d_p)' in thesis
                                      'totalSkill': [0] * parameters.leagueSize,  # create variable team skills, references 'S_i' in thesis
                                      'revenue': [0] * parameters.leagueSize,  # create variable revenue, references 'R_tot_it' in thesis
                                      'hockeyRevenue': parameters.initialTeamBudget,  # create variable hockey related revenue, is initialised with initial team budgets
                                      'wins': [0] * parameters.leagueSize,  # create variable for win count
                                      'games': [0] * parameters.leagueSize,  # create variable for game count
                                      'rank': [0] * parameters.leagueSize,  # create variable for final regular season rank
                                      'eliminatedRS': [0] * parameters.leagueSize,  # create binary variable indicating regular season elimination
                                      'eliminatedPP': [0] * parameters.leagueSize,  # create binary variable indicating pre playoffs elimination
                                      'eliminatedPR1': [0] * parameters.leagueSize,  # create binary variable indicating playoffs round 1 elimination
                                      'eliminatedPR2': [0] * parameters.leagueSize,  # create binary variable indicating playoffs round 2 elimination
                                      'eliminatedPR3': [0] * parameters.leagueSize,  # create binary variable indicating playoffs round 3 elimination
                                      'champion': [0] * parameters.leagueSize,  # create binary variable indicating league champion
                                      'wentBankrupt': [0] * parameters.leagueSize,  # create binary variable indicating if a team went bankrupt
                                      'monetaryFactor': parameters.monetaryFactor,
                                      'marketSize': parameters.marketSize,
                                      'seasonPhaseFactor': parameters.seasonPhaseFactor,
                                      'compBalanceEffect': parameters.compBalanceEffect})
        self.optimalDomesticPlayers = {}
        self.optimalDomesticPlayersSet = set()
        self.optimalDomesticPlayersData = pd.DataFrame()
        self.optimalImportPlayers = {}
        self.finalPlayerSelection = {}
        self.regularSeasonRanking = pd.DataFrame()
        self.leagueCondition = None

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

    def get_salary_cap(self):
        """
        Description:
        Get list of salary caps repeated once for every team

        Returns:
        salaryCapList (list): List of salary cap figure repeated 'leagueSize'-times
        """
        salaryCapList = self.teamData['salaryCap'].tolist()

        return salaryCapList

    def get_effective_team_budgets(self):
        """
        Description:
        Get all team budgets which the teams are effectively able to spend

        Returns:
        effectiveTeamBudgetsList (list): List of all team budgets which teams are effectively able to spend
        """
        effectiveTeamBudgetsList = self.teamData['effectiveBudget'].tolist()

        return effectiveTeamBudgetsList

    def get_team_payrolls(self):
        """
        Description:
        Get all team payrolls

        Returns:
        teamPayrollsList (list): List of all team payrolls
        """
        teamPayrollsList = self.teamData['payroll'].tolist()

        return teamPayrollsList

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

    def get_hockey_related_revenues(self):
        """
        Description:
        Get a list of all hockey related team revenues

        Returns:
        hockeyRevenues (list): List with all hockey related team revenues
        """
        # return all revenues
        hockeyRevenues = self.teamData['hockeyRevenue'].tolist()

        return hockeyRevenues

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
            teamData.loc[teamData['team'] == team, 'wins'] = \
                regularSeasonRanking.loc[regularSeasonRanking['team'] == team, 'wins'].values[0]
            teamData.loc[teamData['team'] == team, 'games'] = \
                regularSeasonRanking.loc[regularSeasonRanking['team'] == team, 'games'].values[0]
            teamData.loc[teamData['team'] == team, 'rank'] = \
                regularSeasonRanking.loc[regularSeasonRanking['team'] == team, 'rank'].values[0]

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
            optimalSelectionSet = set(self.optimalDomesticPlayers[team])

            # create intersection
            intersection = finalSelectionSet.intersection(optimalSelectionSet)

            # print
            print('Team: {}, Total: {}, Set: {}'.format(team, len(intersection), intersection))

    def select_optimal_domestic_players(self, domesticPlayerPool):
        """
        Description:
        Let each team solve the maximization problem of player selection for domestic players

        Input:
        domesticPlayerPool (PlayerPool): The initialised domestic player pool of object DomesticPlayerPool

        Updates:
        self.optimalDomesticPlayers (dict): updates the dictionary with the selected optimal domestic players by each team
        self.optimalDomesticPlayersSet (set): updates the set with all unique domestic players selected over all teams
        self.optimalDomesticPlayersData (set): updates the dataframe with the information about the optimal domestic players
        """

        # initialise new empty dictionary for player selection
        optimalDomesticPlayers = {}

        # get required team information
        teams = self.get_teams()
        teamBudgets = self.get_effective_team_budgets()
        domesticTeamSize = domesticPlayerPool.get_domestic_team_size()

        # for each team in the league
        for team in range(len(teams)):
            # select optimal players based on skill maximization
            selectedPlayers = functions.skill_maximization(domesticPlayerPool, teamBudgets[team], domesticTeamSize)

            # add team as key and the list of selected players as value do the dictionary
            optimalDomesticPlayers[teams[team]] = selectedPlayers.player.tolist()

        # overwrite old dictionary with new dictionary
        self.optimalDomesticPlayers = optimalDomesticPlayers

        # create set of optimal players selected by all teams based on dictionary
        optimalDomesticPlayersSet = set().union(*list(self.optimalDomesticPlayers.values()))

        # overwrite old set with new set, each selected player appears exactly once
        self.optimalDomesticPlayersSet = optimalDomesticPlayersSet

        # import data of all players
        allPlayersData = domesticPlayerPool.allPlayersData

        # extract data from selected players and assign it
        self.optimalDomesticPlayersData = allPlayersData.loc[allPlayersData['player'].isin(self.optimalDomesticPlayersSet)]

    def resolve_player_conflicts(self, domesticPlayerPool):
        """
        Description:
        Assign players which are only picked by one team to that team,
        Resolve conflicts in case players are selected by multiple teams by applying a decision rule which let's
        the player pick a team and let the other teams which were not picked by the players, immediately pick an
        a similarly skilled replacement player

        Input:
        domesticPlayerPool (PlayerPool): An object of class DomesticPlayerPool

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
        self.teamData = functions.update_team_info(self, domesticPlayerPool.allPlayersData)

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
        self.teamData = functions.update_team_info(self, domesticPlayerPool.allPlayersData)

        # for every player which now needs to be replaced by the remaining teams in each conflict
        for player in shuffledConflicts:

            # extract the remaining teams in same conflict order as players have chosen teams
            remainingTeams = shuffledConflicts[player]

            # for each remaining team among the remaining teams in one conflict
            for remainingTeam in remainingTeams:
                # a replacement player for initial player is defined
                replacementPlayer = functions.teams_choose_replacement(player, remainingTeam, domesticPlayerPool, self)

                # if no replacement player can be found because of budget violation
                if replacementPlayer is None:

                    # start next iteration
                    continue

                # add replacement player to the remaining team which has selected the player
                self.finalPlayerSelection = functions.assign_player(self, replacementPlayer, remainingTeam)

                # remove replacement player from available players in player pool
                domesticPlayerPool.remove_player_from_available(replacementPlayer)

            # update team data after each conflict so that it is up to date when resolving next conflict
            self.teamData = functions.update_team_info(self, domesticPlayerPool.allPlayersData)

        assert functions.no_duplicates(self.finalPlayerSelection)

    def select_optimal_import_players(self, foreignPlayerPool, domesticPlayerPool, allowedImports):
        """
        Description:
        Let each team solve the maximization problem of player selection for foreign players

        Input:
        foreignPlayerPool (PlayerPool): The initialised foreign player pool of object ForeignPlayerPool
        domesticPlayerPool (PlayerPool): The initialised domestic player pool of object DomesticPlayerPool
        allowedImports (int): The number of allowed import players

        Updates:
        self.optimalImportPlayers (dict): updates the dictionary with the selected optimal import players by each team
        """
        # create empty dictionary for optimal import players
        optimalImportPlayers = {}

        # get required team information
        teams = self.get_teams()
        teamBudgets = self.get_effective_team_budgets()
        teamPayrolls = self.get_team_payrolls()

        # for each team in the league
        for team in range(len(teams)):

            # calculate remaining budget for imports
            remainingBudget = teamBudgets[team] - teamPayrolls[team]

            # select optimal players based on skill maximization
            selectedPlayers = functions.skill_maximization(foreignPlayerPool, remainingBudget, allowedImports)

            # add selected players to dictionary
            optimalImportPlayers[teams[team]] = selectedPlayers.player.tolist()

        # overwrite old dictionary with new dictionary
        self.optimalImportPlayers = optimalImportPlayers

        # for every team
        for team in teams:
            # for every selected import player
            for player in optimalImportPlayers[team]:
                # assign player to final player selection of teams
                self.finalPlayerSelection = functions.assign_player(self, player, team)

        # combine player data of both player pools for final team update
        combinedPlayersData = pd.concat([domesticPlayerPool.allPlayersData, foreignPlayerPool.allPlayersData], ignore_index=True)

        # update team data after teams are fully stacked
        self.teamData = functions.update_team_info(self, combinedPlayersData)

        # capture potential simulation break conditions:
        # if at least one team does not have have at least minimum amount of players
        if not all(list({team: len(players) >= parameters.teamSizeMin for (team, players) in
                         self.finalPlayerSelection.items()}.values())):

            # warning message
            print("Warning!\nAt least one team has not enough budget to assemble a fully stacked team")

            # extract teams which has not enough budget
            bankruptTeams = list({team: value for (team, value) in {team: len(players) >= parameters.teamSizeMin for (team, players) in
                  self.finalPlayerSelection.items()}.items() if value is False}.keys())

            # report bankrupt teams and break condition
            self.teamData.loc[self.teamData['team'].isin(bankruptTeams), 'wentBankrupt'] = 1

            # define condition and return
            self.leagueCondition = "bankruptcy"

        # Assertions
        assert all(list({team: len(players) <= parameters.teamSizeMax for (team, players) in
                             self.finalPlayerSelection.items()}.values()))  # violation of budget

        assert all([True if self.teamData.loc[x, 'budget'] - self.teamData.loc[x, 'payroll'] > 0 else False for x in
                    range(len(self.teamData))])  # payroll below budget

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
        print("Simulation of regular season")
        self.regularSeasonRanking = functions.simulate_regular_season(self)

        # update team data based on regular season ranking
        self.update_team_data_post_regular_season()

        # simulate playoffs
        print("Simulation of playoffs")
        champion = functions.simulate_playoffs(self)

        print("Champion: ", champion)

    def calculate_season_revenue(self, season):
        """
        Description:
        Calculates the total season revenue of all teams

        Input:
        season (int): Index of current season

        Update:
        self.teamData (dataframe): The dataframe containing team information is updated with final revenue data
        """
        # calculate broadcasting revenue for this season
        currentBroadcastingRevenue = parameters.initialBroadcastingRevenue * (
                1 + parameters.broadcastingRevenueGrowth) ** season

        # calculate hockey related seasonal revenue
        self.teamData['revenue'] += currentBroadcastingRevenue
        self.teamData['hockeyRevenue'] = self.teamData['revenue']

        # add remaining budget to revenue
        self.teamData['revenue'] += self.teamData['budget'] - self.teamData['payroll']

        # round values
        self.teamData['revenue'] = self.teamData['revenue'].round().astype(int)
        self.teamData['hockeyRevenue'] = self.teamData['hockeyRevenue'].round().astype(int)

    def get_player_stats(self, combinedPlayersData):
        """
        Description:
        Calculate and return player stats

        Input:
        combinedPlayersData (int): combined data of all selected players (imports and domestic)

        Return:
        seasonPlayerResults (data frame): Data frame with player stats, one metric per column
        """
        # extract final roster
        finalPlayerSelection = self.finalPlayerSelection

        # create set with all selected players
        selectedPlayerSet = set().union(*list(finalPlayerSelection.values()))

        # extract all data from selected players
        selectedPlayersData = combinedPlayersData.loc[combinedPlayersData["player"].isin(selectedPlayerSet), ]

        # create player stats for selected players
        seasonPlayerResultsSeries = selectedPlayersData["salary"].describe()

        # create data frame in wide format
        seasonPlayerResults = seasonPlayerResultsSeries.to_frame().T

        return seasonPlayerResults

    def reset_for_new_season(self):
        """
        Description:
        Resets the league object for a new season simulation

        Update:
        self.teamData (dataframe): team data is prepared for new season
        self.optimalDomesticPlayers (dict): reset to state of league initialisation
        self.optimalDomesticPlayersSet (set): reset to state of league initialisation
        self.optimalDomesticPlayersData (dataframe): reset to state of league initialisation
        self.finalPlayerSelection (dict): reset to state of league initialisation
        self.regularSeasonRanking (dataframe): reset to state of league initialisation
        """
        # extract new team budgets which is revenue of previous season
        budgets = self.teamData['revenue'].tolist()
        hockeyRevenues = self.teamData['hockeyRevenue'].tolist()

        # update teamData
        self.teamData = pd.DataFrame({'team': parameters.teams,
                                      'domestics': [0] * parameters.leagueSize,  # the number of domestic players
                                      'imports': [0] * parameters.leagueSize,  # the number of import players
                                      'budget': budgets,  # team budgets based on previous season revenues, references 'R_tot_it-1',
                                      'salaryCap': [False] * parameters.leagueSize,  # create variable salary cap, references 'R_cap'
                                      'effectiveBudget': [0] * parameters.leagueSize,  # create variable for the budget teams are allowed to spend
                                      'payroll': [0] * parameters.leagueSize,  # create variable team payrolls, references 'sum(W_p * d_p)' in thesis
                                      'totalSkill': [0] * parameters.leagueSize,  # create variable team skills, references 'S_i' in thesis
                                      'revenue': [0] * parameters.leagueSize,  # create variable revenue, references 'R_tot_it' in thesis
                                      'hockeyRevenue': hockeyRevenues,  # update hockey related revenues
                                      'wins': [0] * parameters.leagueSize,  # create variable for win count
                                      'games': [0] * parameters.leagueSize,  # create variable for game count
                                      'rank': [0] * parameters.leagueSize,  # create variable for final regular season rank
                                      'eliminatedRS': [0] * parameters.leagueSize,  # create binary variable indicating regular season elimination
                                      'eliminatedPP': [0] * parameters.leagueSize,  # create binary variable indicating pre playoffs elimination
                                      'eliminatedPR1': [0] * parameters.leagueSize,  # create binary variable indicating playoffs round 1 elimination
                                      'eliminatedPR2': [0] * parameters.leagueSize,  # create binary variable indicating playoffs round 2 elimination
                                      'eliminatedPR3': [0] * parameters.leagueSize,  # create binary variable indicating playoffs round 3 elimination
                                      'champion': [0] * parameters.leagueSize,  # create binary variable indicating league champion
                                      'wentBankrupt': [0] * parameters.leagueSize,  # create binary variable indicating if a team went bankrupt
                                      'monetaryFactor': parameters.monetaryFactor,
                                      'marketSize': parameters.marketSize,
                                      'seasonPhaseFactor': parameters.seasonPhaseFactor,
                                      'compBalanceEffect': parameters.compBalanceEffect})
        self.optimalDomesticPlayers = {}
        self.optimalDomesticPlayersSet = set()
        self.optimalDomesticPlayersData = pd.DataFrame()
        self.optimalImportPlayers = {}
        self.finalPlayerSelection = {}
        self.regularSeasonRanking = pd.DataFrame()
        self.leagueCondition = None
