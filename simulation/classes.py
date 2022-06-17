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
            self.k (int): determines pool size (number of available players)
            self.p (numpy array): determines the ID's of players
            self.S_p (numpy array): determines the skill level of players
            self.W_p (numpy array): determines the salary of players
            self.remainingPlayerSet (set): empty set which is updated when players from the pool are selected
        """
        self.k = k_new
        self.p = np.arange(start=1, stop=k_new + 1)  # create id's from 1 to k_new
        self.S_p = np.round(np.random.beta(a=alpha, b=beta, size=k_new), 2)  # draw skill from beta distribution
        self.W_p = np.round(w_max * self.S_p * (1 - ((k_new - k_old) / k_old)))  # calculate salary
        self.remainingPlayersSet = set()

    def get_player_id(self):
        """
        Description:
        Get player ID's in a list

        Returns:
        playerIDList (list)
        """
        playerIDList = self.p.tolist()

        return playerIDList

    def get_player_skill(self):
        """
        Description:
        Get player skills in a list

        Returns:
        playerSkillList (list)
        """
        playerSkillList = self.S_p.tolist()

        return playerSkillList

    def get_player_salary(self):
        """
        Description:
        Get player salaries in a list

        Returns:
        playerSalaryList (list)
        """
        playerSalaryList = self.W_p.tolist()

        return playerSalaryList

    def get_data(self):
        """
        Description:
        Get player pool as data set

        Returns:
        player_data (pandas dataframe)
        """
        player_data = pd.DataFrame(
            data=np.column_stack((self.p, self.S_p, self.W_p)),  # arrays as columns
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
        self.p (array): remove all players from array which were selected in the maximization process
        self.S_p (array): remove all skills of selected players from the array
        self.W_p (array): remove all salaries of selected players from the array
        self.remainingPlayersSet (set): create a set of all remaining players after maximization process
        """

        # convert set to a list
        optimalPlayersList = list(optimalPlayersSet)

        # obtain index of optimal players by subtracting one from id
        optimalPlayersList = [i - 1 for i in optimalPlayersList]

        # remove players from player pool
        self.p = np.delete(self.p, optimalPlayersList)  # remove players from p
        self.S_p = np.delete(self.S_p, optimalPlayersList)  # remove players from S_p
        self.W_p = np.delete(self.W_p, optimalPlayersList)  # remove players from W_p

        # create a set of remaining players
        self.remainingPlayersSet = set(self.p)

        # assert that there is no intersection between the remaining and selected players
        assert len(self.remainingPlayersSet.intersection(optimalPlayersSet)) == 0

    def remove_player_from_available(self, player):
        """
        Description:
        Remove a single player selected by a team from the pool of available players

        Input:
        player (int): the player to be removed from the available players

        Update:
        self.p (array): remove selected player from the array
        self.S_p (array): remove skill of selected player from the array
        self.W_p (array): remove salary of selected player from the array
        self.remainingPlayersSet (set): create a set of all remaining players after a player is selected
        """

        # identify index of player to be removed in arrays
        playerIndex = np.where(self.p == player)[0][0]

        # remove players from player pool
        self.p = np.delete(self.p, playerIndex)  # remove player from p
        self.S_p = np.delete(self.S_p, playerIndex)  # remove player from S_p
        self.W_p = np.delete(self.W_p, playerIndex)  # remove player from W_p

        # create a set of remaining players
        self.remainingPlayersSet = set(self.p)


# define league as class
class League(object):
    def __init__(self):
        """
        Description:
        Initializes a league object. The object is fully initialised based on parameters

        A league object has the following attributes:
            self.i (list): determines the teams in the league
            self.R_tot_i0 (list): determines the starting revenues of teams before first season
            self.teamData (dataframe): dataframe with information about the team
            self.optimalPlayers (dict): dictionary which is filled when players are selected in maximization process, empty when intialised
            self.optimalPlayersSet (set): set which is filled when players are selected in maximization processs, empty when initialised
            self.optimalPlayersData (dataframe): dataframe which is filled when players are selected in maximization process, empty when initialised
            self.finalPlayerSelection (dict): dictionary which is filled with final player selection per team when player conflicts are resolved
        """
        self.i = ['team' + str(i + 1) for i in range(n)]  # create n teams
        self.R_tot_i0 = np.round(np.random.uniform(low=10 * w_max, high=15 * w_max, size=n))  # create team revenues
        self.teamData = pd.DataFrame({'team': self.i, 'budget': self.R_tot_i0, 'payroll': [0] * n})
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
        optimalPlayersSet = set()
        optimalPlayersData = pd.DataFrame()

        # for loop to select optimal players for each team and write them to a list
        for i in range(len(self.i)):
            # select optimal players based on skill maximization
            selectedPlayers = functions.skill_maximization(playerPool, self.R_tot_i0[i])

            # create team entry with ID's of players
            optimalPlayers[self.i[i]] = selectedPlayers.ID.tolist()

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
        self.finalPlayerSelection = {team: [] for team in self.i}

        # for each player without conflict
        for p in noConflicts:
            # define the team, the player is going to join
            i = noConflicts[p][0]

            # assign the player to the according team
            self.finalPlayerSelection = functions.assign_player(self.finalPlayerSelection, p, i)

        # update payroll data for all teams
        self.teamData = functions.update_team_payroll(self.finalPlayerSelection, self.teamData, playerInfo)

        # for each player with conflict
        for p in conflicts:

            # define the potential teams a player can join
            I = conflicts[p]

            # let the player decide which team to join
            i = functions.player_chooses_team(I)

            # assign the player to the team he decided to join
            self.finalPlayerSelection = functions.assign_player(self.finalPlayerSelection, p, i)

            # remove picked team from list of potential teams
            I.remove(i)

            # shuffle the remaining teams so that teams can pick a replacement in a random order
            ra.shuffle(I)

            # For every remaining team
            for j in I:
                # search an choose a player
                q = functions.teams_choose_replacement(p, j, self.optimalPlayersData, playerPool.get_data(),
                                                       self.teamData)

                # add replacement player to the final list of selected players
                self.finalPlayerSelection = functions.assign_player(self.finalPlayerSelection, q, j)

                # remove replacement player from available players in player pool
                playerPool.remove_player_from_available(q)

            # update payroll data after each conflict so that it is up to date when resolving next conflict
            self.teamData = functions.update_team_payroll(self.finalPlayerSelection, self.teamData, playerInfo)

        # assert that constraints also hold in final player selection
        assert all(list({k: len(v) == h for (k, v) in
                         self.finalPlayerSelection.items()}.values()))  # all teams have the defined number of players
        assert all([True if self.teamData.loc[x, 'budget'] - self.teamData.loc[x, 'payroll'] > 0 else False for x in
                    range(len(self.teamData))])  # payroll below budget

        # return new player pool object
        return playerPool
