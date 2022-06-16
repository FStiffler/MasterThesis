from parameters import *
from functions import skill_maximization
import numpy as np
import pandas as pd


# define player pool as class
class PlayerPool(object):
    def __init__(self):
        '''
        Initializes the player pool object
        The object is fully initialised based on parameters
        A player pool object has the following attributes:
            self.k (int): determines pool size (number of available players)
            self.p (numpy array): determines the ID's of players
            self.S_p (numpy array): determines the skill level of players
            self.W_p (numpy array): determines the salary of players
        '''
        self.k = k_new
        self.p = np.arange(start=1, stop=k_new + 1)  # create id's from 1 to k_new
        self.S_p = np.round(np.random.beta(a=alpha, b=beta, size=k_new), 2)  # draw skill from beta distribution
        self.W_p = np.round(w_max * self.S_p * (1 - ((k_new - k_old) / k_old)))  # calculate salary

    def get_player_id(self):
        '''
        Get player ID's in a list
        Returns: playerIDList (list)
        '''
        playerIDList = self.p.tolist()

        return playerIDList

    def get_player_skill(self):
        '''
        Get player skills in a list
        Returns: playerSkillList (list)
        '''
        playerSkillList = self.S_p.tolist()

        return playerSkillList

    def get_player_salary(self):
        '''
        Get player salaries in a list
        Returns: playerSalaryList (list)
        '''
        playerSalaryList = self.W_p.tolist()

        return playerSalaryList


    def get_data(self):
        '''
        Get player pool as data set
        Returns: player_data (pandas dataframe)
        '''
        player_data = pd.DataFrame(
            data=np.column_stack((self.p, self.S_p, self.W_p)),  # arrays as columns
            columns=["ID", "Skill", "Salary"]
        )
        player_data = player_data.astype({"ID": int})  # change ID to integer

        return player_data


# define league as class
class League(object):
    def __init__(self):
        '''
        Initializes a league object
        The object is fully initialised based on parameters
        A league object has the following attributes:
            self.i (list): determines the teams in the league
            self.R_tot_i0 (list): determines the starting revenues of teams before first season
            self.optimalPlayers {dict}: empty dictionary which is filled when players are selected in maximization process

        '''
        self.i = ['team'+str(i+1) for i in range(n)]  # create n teams
        self.R_tot_i0 = np.round(np.random.uniform(low=10*w_max, high=15*w_max, size=n))  # create team revenues
        self.optimalPlayers = {}

    def select_optimal_players(self, playerPool):
        '''
        Let each team solve the maximization problem of player selection
        Input:
        playerPool (PlayerPool): An object of class PlayerPool
        Returns:

        '''
        # initialise new empty dictionary for player selection
        optimalPlayers = {}

        # for loop to select optimal players for each team and write them to a list
        for i in range(len(self.i)):

            # select optimal players based on skill maximization
            selectedPlayers = skill_maximization(playerPool, self.R_tot_i0[i])

            # create team entry with ID's of players
            optimalPlayers[self.i[i]] = selectedPlayers.ID.tolist()

            # overwrite old dictionary with new dictionary
            self.optimalPlayers = optimalPlayers
