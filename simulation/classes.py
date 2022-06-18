from parameters import *
import functions
import numpy as np
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
            self.allPlayers (array): All players in player pool
            self.allPlayerSkills (array): All skill levels of players in player pool
            self.allPlayerSalaries (array): All salaries in the player pool
            self.allPlayersData (dataframe): A dataframe with information about all players, initialised by the method self.get_player_data
            self.availablePlayers (array): Available players yet picked by a team, is initialised with all players
            self.availablePlayerSkills (array): Available skill levels players not yet picked by a team, is initialised with all skill levels
            self.availablePlayerSalaries (array): Available salaries of players not yet picked by a team, is initialised with all salaries
            self.availablePlayerSet (set): Set of available players, is initialised with all players
            self.availablePlayersData (dataframe): A dataframe with information about available players not yet picked by a team initialised by the method self.get_player_data
        """
        self.size = newPlayerPoolSize
        self.allPlayers = np.arange(start=1, stop=newPlayerPoolSize + 1)  # create id's from 1 to newPlayerPoolSize
        self.allPlayerSkills = np.round(np.random.beta(a=alpha, b=beta, size=newPlayerPoolSize),
                                        2)  # draw skill from beta distribution
        self.allPlayerSalaries = np.round(maximalSalary * self.allPlayerSkills * (
                    1 - ((newPlayerPoolSize - oldPlayerPoolSize) / oldPlayerPoolSize)))  # calculate salary
        self.allPlayersData = self.get_all_player_data()
        self.availablePlayers = self.allPlayers
        self.availablePlayerSkills = self.allPlayerSkills
        self.availablePlayerSalaries = self.allPlayerSalaries
        self.availablePlayersSet = set(self.allPlayers)
        self.availablePlayersData = self.get_available_player_data()

    def get_all_players(self):
        """
        Description:
        Get all players as list

        Returns:
        allPlayersList (list): List of all players
        """
        allPlayersList = self.allPlayers.tolist()

        return allPlayersList

    def get_all_player_skills(self):
        """
        Description:
        Get skill levels of all players as list

        Returns:
        allPlayerSkillsList (list) : List of skill levels of all players
        """
        allPlayerSkillsList = self.allPlayerSkills.tolist()

        return allPlayerSkillsList

    def get_all_player_salaries(self):
        """
        Description:
        Get all player salaries as a list

        Returns:
        allPlayerSalariesList (list): List of salaries of all players
        """
        allPlayerSalariesList = self.allPlayerSalaries.tolist()

        # convert to integer
        allPlayerSalariesList = [int(salary) for salary in allPlayerSalariesList]

        return allPlayerSalariesList

    def get_all_player_data(self):
        """
        Description:
        Get all player information as data frame

        Returns:
        allPlayersData (dataframe): Dataframe with information about all players
        """
        allPlayersData = pd.DataFrame(
            data=np.column_stack((self.allPlayers, self.allPlayerSkills, self.allPlayerSalaries)),  # arrays as columns
            columns=["ID", "Skill", "Salary"]
        )
        allPlayersData = allPlayersData.astype({"ID": int, 'Salary': int})  # change ID to integer

        return allPlayersData

    def get_available_players(self):
        """
        Description:
        Get available players as list

        Returns:
        availablePlayersList (list): List of available players
        """
        availablePlayersList = self.availablePlayers.tolist()

        return availablePlayersList

    def get_available_player_skills(self):
        """
        Description:
        Get skill levels of available players as list

        Returns:
        availablePlayerSkillsList (list) : List of skill levels of available players
        """
        availablePlayerSkillsList = self.availablePlayerSkills.tolist()

        return availablePlayerSkillsList

    def get_available_player_salaries(self):
        """
        Description:
        Get available player salaries as a list

        Returns:
        availablePlayerSalariesList (list): List of salaries of available players
        """
        availablePlayerSalariesList = self.availablePlayerSalaries.tolist()

        # convert to integer
        availablePlayerSalariesList = [int(salary) for salary in availablePlayerSalariesList]

        return availablePlayerSalariesList

    def get_available_player_data(self):
        """
        Description:
        Get available player information as data frame

        Returns:
        availablePlayersData (dataframe): Dataframe with information about available players
        """
        availablePlayersData = pd.DataFrame(
            data=np.column_stack((self.availablePlayers, self.availablePlayerSkills, self.availablePlayerSalaries)),
            # arrays as columns
            columns=["ID", "Skill", "Salary"]
        )
        availablePlayersData = availablePlayersData.astype({"ID": int, 'Salary': int})  # change ID to integer

        return availablePlayersData

    def update_player_pool_after_maximization(self, optimalPlayersSet):
        """
        Description:
        Update the players in the player pool after teams have selected optimal players in maximization process

        Input:
        optimalPlayersSet (set): the set of optimal players chosen by all teams derived from an object with class League
        after calling the class method select_optimal_players

        Update:
        self.availablePlayers (array): Remove all players from available which were selected in the maximization process
        self.availablePlayerSkills (array): Remove all skill levels of players selected in the maximization process from available
        self.availablePlayerSalaries (array): Remove all salaries of players selected in the maximization process from available
        self.availablePlayersSet (set): Update set of available players
        """

        # convert set to a list
        optimalPlayersList = list(optimalPlayersSet)

        # obtain index list of optimal players by subtracting one from player id
        optimalPlayersIndex = [player - 1 for player in optimalPlayersList]

        # remove optimal players from available players since they are no longer available
        self.availablePlayers = np.delete(self.availablePlayers, optimalPlayersIndex)  # remove optimal players
        self.availablePlayerSkills = np.delete(self.availablePlayerSkills,
                                               optimalPlayersIndex)  # remove skill levels of optimal players
        self.availablePlayerSalaries = np.delete(self.availablePlayerSalaries,
                                                 optimalPlayersIndex)  # remove salaries of optimal players

        # create a set of still available players
        self.availablePlayersSet = set(self.availablePlayers)

        # update data on available players
        self.availablePlayersData = self.get_available_player_data()

        # assert that there is no intersection between the still available and the selected players
        assert len(self.availablePlayersSet.intersection(optimalPlayersSet)) == 0

    def remove_player_from_available(self, player):
        """
        Description:
        Remove a single player selected by a team as replacement from the pool of available players

        Input:
        player (int): The selected player to be removed from the available players

        Update:
        self.availablePlayers (array): Remove player from array of available players
        self.availablePlayerSkills (array): Remove skill level of selected player from the array
        self.availablePlayerSalaries (array): Remove salary of selected player from the array
        self.availablePlayersSet (set): Update set of available players
        self.availablePlayersData (dataframe): Update information of available players in dataframe
        """

        # identify index of player to be removed in arrays
        playerIndex = np.where(self.availablePlayers == player)[0][0]

        # remove player and all attributes from available players and their attributes
        self.availablePlayers = np.delete(self.availablePlayers, playerIndex)
        self.availablePlayerSkills = np.delete(self.availablePlayerSkills, playerIndex)
        self.availablePlayerSalaries = np.delete(self.availablePlayerSalaries, playerIndex)

        # update set of remaining players
        self.availablePlayersSet = set(self.availablePlayers)

        # update data on available players
        self.availablePlayersData = self.get_available_player_data()


# define league as class
class League(object):
    def __init__(self):
        """
        Description:
        Initializes a league object. The object is fully initialised based on parameters

        A league object has the following attributes:
            self.teams (list): determines the teams in the league
            self.teamBudgets (list): determines the starting revenues of teams before first season
            self.teamData (dataframe): dataframe with information about the team
            self.optimalPlayers (dict): dictionary which is filled when players are selected in maximization process
            self.optimalPlayersSet (set): set which is filled when players are selected in maximization process
            self.optimalPlayersData (dataframe): dataframe which is filled when players are selected in maximization process
            self.finalPlayerSelection (dict): dictionary which is filled with final player selection per team when player conflicts are resolved
        """
        self.teams = ['team' + str(i + 1) for i in range(leagueSize)]  # create n teams
        self.teamBudgets = np.round(
            np.random.uniform(low=7 * maximalSalary, high=15 * maximalSalary, size=leagueSize)).astype(int)  # create team revenues
        self.teamData = pd.DataFrame({'team': self.teams, 'budget': self.teamBudgets, 'payroll': [0] * leagueSize, 'totalSkill': [0] * leagueSize})
        self.optimalPlayers = {}
        self.optimalPlayersSet = set()
        self.optimalPlayersData = pd.DataFrame()
        self.finalPlayerSelection = {}

    def select_optimal_players(self, playerPool):
        """
        Description:
        Let each team solve the maximization problem of player selection

        Input:
        playerPool (PlayerPool): A player pool of object PlayerPool

        Updates:
        self.optimalPlayers (dict): updates the dictionary with the selected optimal players by each team
        self.optimalPlayersSet (set): updates the set with all unique players selected over all teams
        """

        # initialise new empty dictionary for player selection
        optimalPlayers = {}

        # for each team in the league
        for team in range(len(self.teams)):
            # select optimal players based on skill maximization
            selectedPlayers = functions.skill_maximization(playerPool, self.teamBudgets[team])

            # add team as key and the list of selected players as value do the dictionary
            optimalPlayers[self.teams[team]] = selectedPlayers.ID.tolist()

        # overwrite old dictionary with new dictionary
        self.optimalPlayers = optimalPlayers

        # create set of optimal players selected by all teams based on dictionary
        optimalPlayersSet = set().union(*list(self.optimalPlayers.values()))

        # overwrite old set with new set, each selected player appears exactly once
        self.optimalPlayersSet = optimalPlayersSet

        # import data of all players
        allPlayersData = playerPool.get_all_player_data()

        # extract data from selected players and assign it
        self.optimalPlayersData = allPlayersData.loc[allPlayersData['ID'].isin(self.optimalPlayersSet)]

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
        # identify conflicts and non conflicts
        conflicts, noConflicts = functions.identify_conflicts(self.optimalPlayers, self.optimalPlayersSet)

        # shuffle conflicts
        shuffledConflicts = functions.shuffle_conflicts(conflicts)

        # initialise dictionary for final player selection by adding a key for each team and empty lists as values
        self.finalPlayerSelection = {team: [] for team in self.teams}

        # for each player without conflict
        for player in noConflicts:
            # define the team which has selected the player
            team = noConflicts[player][0]

            # assign the player to the according team
            self.finalPlayerSelection = functions.assign_player(self.finalPlayerSelection, player, team)

        # update data for all teams
        self.teamData = functions.update_team_info(self.finalPlayerSelection, self.teamData,
                                                      playerPool.get_all_player_data())

        # for each player with conflict
        for player in shuffledConflicts:

            # define the potential teams a player can choose
            interestedTeams = shuffledConflicts[player]

            # let the player decide which team to join
            chosenTeam = functions.player_chooses_team(interestedTeams)

            # assign the player to the team he decided to join
            self.finalPlayerSelection = functions.assign_player(self.finalPlayerSelection, player, chosenTeam)

            # remove chosen team from list of interested teams
            interestedTeams.remove(chosenTeam)

            # shuffle the remaining teams so that teams can pick a replacement in a random order
            ra.shuffle(interestedTeams)

            # For every remaining team
            for remainingTeam in interestedTeams:
                # a replacement player for initial player is defined
                replacementPlayer = functions.teams_choose_replacement(player, remainingTeam,
                                                                       playerPool.get_all_player_data(),
                                                                       playerPool.get_available_player_data(),
                                                                       self.teamData)

                # add replacement player to the remaining team which has selected the player
                self.finalPlayerSelection = functions.assign_player(self.finalPlayerSelection, replacementPlayer,
                                                                    remainingTeam)

                # remove replacement player from available players in player pool
                playerPool.remove_player_from_available(replacementPlayer)

            # update team data after each conflict so that it is up to date when resolving next conflict
            self.teamData = functions.update_team_info(self.finalPlayerSelection, self.teamData,
                                                          playerPool.allPlayersData)

        # assert that constraints also hold in final player selection
        assert all(list({team: len(players) == teamSize for (team, players) in
                         self.finalPlayerSelection.items()}.values()))  # all teams have the defined number of players
        assert all([True if self.teamData.loc[x, 'budget'] - self.teamData.loc[x, 'payroll'] > 0 else False for x in
                    range(len(self.teamData))])  # payroll below budget
        assert functions.no_duplicates(self.finalPlayerSelection)

        # return new player pool object
        return playerPool

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
