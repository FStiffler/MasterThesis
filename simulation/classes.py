import parameters
import functions
import pandas as pd
import random as ra


# define player pool as class
class PlayerPool(object):
    def __init__(self):
        """
        Description:
        Initializes the player pool object. The object is fully initialised based on parameters

        A player pool object has the following attributes:
            self.size (int): Determines pool size (number of available players)
            self.allPlayersData (dataframe): A dataframe with information about all initialised players, infos are to be found in parameter file
            self.availablePlayersData (dataframe): A dataframe with information about available players not yet picked by a team, initialised with all players
        """
        self.size = parameters.newPlayerPoolSize
        self.allPlayersData = functions.get_all_player_data()
        self.availablePlayersData = functions.get_all_player_data()

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


# define league as class
class League(object):
    def __init__(self):
        """
        Description:
        Initializes a league object. The object is fully initialised based on parameters

        A league object has the following attributes:
            self.teamData (dataframe): Dataframe with information about the team, information about the parameters are to be found in the parameters file
            self.optimalPlayers (dict): Dictionary with each team as key and a list of optimal players selected by the team in maximization process, is initialised empty
            self.optimalPlayersSet (set): Set containing every selected player in the maximization process once, is initialised empty
            self.optimalPlayersData (dataframe): Dataframe containing information about the selected players in maximization process, is initialised empty
            self.finalPlayerSelection (dict): Dictionary with each team as key and a list of the final players selected by the team in replacement process, is initialised empty
            self.regularSeasonRanking (dataframe): Dataframe which contains regular season ranking, is initialised empty
        """
        self.teamData = pd.DataFrame({'team': parameters.teams,
                                      'budget': parameters.teamBudgets,
                                      'payroll': [0] * parameters.leagueSize,
                                      'totalSkill': [0] * parameters.leagueSize,
                                      'revenue': [0] * parameters.leagueSize,
                                      'marketPotential': parameters.marketSize,
                                      'playoffFactor': parameters.seasonPhaseFactor,
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

    def get_skill_dictionary(self):
        """
        Description:
        Get a dictionary of teams and their according skill levels

        Returns:
        skillDictionary (list): Dictionary with team as key and team skill as value
        """
        # get required team information
        teams = self.get_teams()
        skills = self.get_team_skills()

        # create skill dictionary
        skillDictionary = {teams[team]: round(skills[team], 2) for team in range(len(teams))}

        return skillDictionary

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

        # simulate playoffs
        champion = functions.simulate_playoffs(self)

        print(champion)
