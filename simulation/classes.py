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
            self.size (int): determines pool size (number of available players)
            self.players (numpy array): determines the ID's of players
            self.playerSkills (numpy array): determines the skill level of players
            self.playerSalaries (numpy array): determines the salary of players
            self.remainingPlayerSet (set): empty set which is updated when players from the pool are selected
        """
        self.size = newPlayerPoolSize
        self.players = np.arange(start=1, stop=newPlayerPoolSize + 1)  # create id's from 1 to newPlayerPoolSize
        self.playerSkills = np.round(np.random.beta(a=alpha, b=beta, size=newPlayerPoolSize), 2)  # draw skill from beta distribution
        self.playerSalaries = np.round(maximalSalary * self.playerSkills * (1 - ((newPlayerPoolSize - oldPlayerPoolSize) / oldPlayerPoolSize)))  # calculate salary
        self.remainingPlayersSet = set()

    def get_players(self):
        """
        Description:
        Get player ID's in a list

        Returns:
        playerIDList (list)
        """
        playerIDList = self.players.tolist()

        return playerIDList

    def get_player_skills(self):
        """
        Description:
        Get player skills in a list

        Returns:
        playerSkillList (list)
        """
        playerSkillList = self.playerSkills.tolist()

        return playerSkillList

    def get_player_salaries(self):
        """
        Description:
        Get player salaries in a list

        Returns:
        playerSalaryList (list)
        """
        playerSalaryList = self.playerSalaries.tolist()

        return playerSalaryList

    def get_data(self):
        """
        Description:
        Get player pool as data set

        Returns:
        player_data (pandas dataframe)
        """
        player_data = pd.DataFrame(
            data=np.column_stack((self.players, self.playerSkills, self.playerSalaries)),  # arrays as columns
            columns=["ID", "Skill", "Salary"]
        )
        player_data = player_data.astype({"ID": int})  # change ID to integer

        return player_data

    def update_player_pool_after_maximization(self, optimalPlayersSet):
        """
        Description:
        Update the players in the player pool after teams have selected optimal players in maximization process

        Input:
        optimalPlayersSet (set): the set of optimal players chosen by all teams derived from an object with class League
        after calling the class method select_optimal_players

        Update:
        self.players (array): remove all players from array which were selected in the maximization process
        self.playerSkills (array): remove all skills of selected players from the array
        self.playerSalaries (array): remove all salaries of selected players from the array
        self.remainingPlayersSet (set): create a set of all remaining players after maximization process
        """

        # convert set to a list
        optimalPlayersList = list(optimalPlayersSet)

        # obtain index of optimal players by subtracting one from id
        optimalPlayersIndex = [player - 1 for player in optimalPlayersList]

        # remove players from player pool
        self.players = np.delete(self.players, optimalPlayersIndex)  # remove players from p
        self.playerSkills = np.delete(self.playerSkills, optimalPlayersIndex)  # remove players from S_p
        self.playerSalaries = np.delete(self.playerSalaries, optimalPlayersIndex)  # remove players from W_p

        # create a set of remaining players
        self.remainingPlayersSet = set(self.players)

        # assert that there is no intersection between the remaining and selected players
        assert len(self.remainingPlayersSet.intersection(optimalPlayersSet)) == 0

    def remove_player_from_available(self, player):
        """
        Description:
        Remove a single player selected by a team from the pool of available players

        Input:
        player (int): the player to be removed from the available players

        Update:
        self.players (array): remove selected player from the array
        self.playerSkills (array): remove skill of selected player from the array
        self.playerSalaries (array): remove salary of selected player from the array
        self.remainingPlayersSet (set): create a set of all remaining players after a player is selected
        """

        # identify index of player to be removed in arrays
        playerIndex = np.where(self.players == player)[0][0]

        # remove players from player pool
        self.players = np.delete(self.players, playerIndex)  # remove player from p
        self.playerSkills = np.delete(self.playerSkills, playerIndex)  # remove player from S_p
        self.playerSalaries = np.delete(self.playerSalaries, playerIndex)  # remove player from W_p

        # create a set of remaining players
        self.remainingPlayersSet = set(self.players)


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
            self.optimalPlayersSet (set): set which is filled when players are selected in maximization processs
            self.optimalPlayersData (dataframe): dataframe which is filled when players are selected in maximization process
            self.finalPlayerSelection (dict): dictionary which is filled with final player selection per team when player conflicts are resolved
        """
        self.teams = ['team' + str(i + 1) for i in range(leagueSize)]  # create n teams
        self.teamBudgets = np.round(np.random.uniform(low=10 * maximalSalary, high=15 * maximalSalary, size=leagueSize))  # create team revenues
        self.teamData = pd.DataFrame({'team': self.teams, 'budget': self.teamBudgets, 'payroll': [0] * leagueSize})
        self.optimalPlayers = {}
        self.optimalPlayersSet = set()
        self.optimalPlayersData = pd.DataFrame()
        self.finalPlayerSelection = {}

    def select_optimal_players(self, playerPool):
        """
        Description:
        Let each team solve the maximization problem of player selection

        Input:
        playerPool (PlayerPool): An object of class PlayerPool

        Updates:
        self.optimalPlayers (dict): updates the dictionary with the selected optimal players by each team
        self.optimalPlayersSet (set): updates the set with all unique players selected over all teams
        """
        # initialise new empty dictionary for player selection
        optimalPlayers = {}

        # for loop to select optimal players for each team and write them to a list
        for team in range(len(self.teams)):

            # select optimal players based on skill maximization
            selectedPlayers = functions.skill_maximization(playerPool, self.teamBudgets[team])

            # create team entry with ID's of players
            optimalPlayers[self.teams[team]] = selectedPlayers.ID.tolist()

        # overwrite old dictionary with new dictionary
        self.optimalPlayers = optimalPlayers

        # create set of optimal players based on dictionary
        optimalPlayersSet = set().union(*list(self.optimalPlayers.values()))

        # overwrite old set with new set, each selected player appears exactly once
        self.optimalPlayersSet = optimalPlayersSet

        # import data of all players
        playerData = playerPool.get_data()

        # extract data from selected players
        self.optimalPlayersData = playerData.loc[playerData['ID'].isin(self.optimalPlayersSet)]

    def resolve_player_conflicts(self, playerPool, playerInfo):
        """
        Description:
        Assign players which are only picked by one team to that team,
        Resolve conflicts in case players are selected by multiple teams by applying a decision rule which let's
        the player pick a team and let the other teams which were not picked by the players, immediately pick an
        a similarly skilled replacement player

        Input:
        playerPool (PlayerPool): An object of class PlayerPool
        playerInfo (dataframe): A dataframe which contains information about all existing players

        Updates:
        playerPool (PlayerPool): The selected replacement players are removed from available players in player pool
        self.finalPlayerSelection (dict): The dictionary with the final player selection is completed
        self.teamData (dataframe): The dataframe with information about the teams is completed
        """
        # identify conflicts and non conflicts
        conflicts, noConflicts = functions.identify_conflicts(self.optimalPlayers, self.optimalPlayersSet)

        # initialise final player selection by entering each team with an empty player list
        self.finalPlayerSelection = {team: [] for team in self.teams}

        # for each player without conflict
        for player in noConflicts:

            # define the team which has selected the player
            team = noConflicts[player][0]

            # assign the player to the according team
            self.finalPlayerSelection = functions.assign_player(self.finalPlayerSelection, player, team)

        # update payroll data for all teams
        self.teamData = functions.update_team_payroll(self.finalPlayerSelection, self.teamData, playerInfo)

        # for each player with conflict
        for player in conflicts:

            # define the potential teams a player can join
            interestedTeams = conflicts[player]

            # let the player decide which team to join
            selectedTeam = functions.player_chooses_team(interestedTeams)

            # assign the player to the team he decided to join
            self.finalPlayerSelection = functions.assign_player(self.finalPlayerSelection, player, selectedTeam)

            # remove picked team from list of interested teams
            interestedTeams.remove(selectedTeam)

            # shuffle the remaining teams so that teams can pick a replacement in a random order
            ra.shuffle(interestedTeams)

            # For every remaining team
            for remainingTeam in interestedTeams:

                # a replacement player for initial player is defined
                replacementPlayer = functions.teams_choose_replacement(player, remainingTeam, self.optimalPlayersData, playerPool.get_data(), self.teamData)

                # add replacement player to the remaining team which has selected the player
                self.finalPlayerSelection = functions.assign_player(self.finalPlayerSelection, replacementPlayer, remainingTeam)

                # remove replacement player from available players in player pool
                playerPool.remove_player_from_available(replacementPlayer)

            # update payroll data after each conflict so that it is up to date when resolving next conflict
            self.teamData = functions.update_team_payroll(self.finalPlayerSelection, self.teamData, playerInfo)


        # assert that constraints also hold in final player selection
        assert all(list({team: len(players) == teamSize for (team, players) in self.finalPlayerSelection.items()}.values()))  # all teams have the defined number of players
        assert all([True if self.teamData.loc[x, 'budget'] - self.teamData.loc[x, 'payroll'] > 0 else False for x in range(len(self.teamData))])  # payroll below budget

        # return new player pool object
        return playerPool
