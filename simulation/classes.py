from parameters import *
import numpy as np
import pandas as pd


# define player pool as class
class PlayerPool(object):
    def __init__(self):
        '''
        Initializes the player pool object
        The object is fully initialised based on parameters
        A player pool object has the following attributes:
            self.size (int): determines pool size (number of available players)
            self.playerID (numpy array): determines the ID's of players
            self.playerSkill (numpy array): determines the skill level of players
            self.playerSalary (numpy array): determines the salary of players
        '''
        self.size = k_new
        self.playerID = np.arange(start=1, stop=k_new + 1)  # create id's from 1 to k_new
        self.playerSkill = np.round(np.random.beta(a=alpha, b=beta, size=k_new), 2)  # draw skill from beta distribution
        self.playerSalary = np.round(w_max * self.playerSkill * (1 - ((k_new - k_old) / k_old)))  # calculate salary

    def get_playerID(self):
        '''
        Get player ID's in a list
        Returns: playerIDList (list)
        '''
        playerIDList = self.playerID.tolist()

        return playerIDList

    def get_playerSkill(self):
        '''
        Get player skills in a list
        Returns: playerSkillList (list)
        '''
        playerSkillList = self.playerSkill.tolist()

        return playerSkillList

    def get_playerSalary(self):
        '''
        Get player salaries in a list
        Returns: playerSalaryList (list)
        '''
        playerSalaryList = self.playerSalary.tolist()

        return playerSalaryList


    def get_data(self):
        '''
        Get player pool as data set
        Returns: player_data (pandas dataframe)
        '''
        player_data = pd.DataFrame(
            data=np.column_stack((self.playerID, self.playerSkill, self.playerSalary)),  # arrays as columns
            columns=["ID", "Skill", "Salary"]
        )
        player_data = player_data.astype({"ID": int})  # change ID to integer

        return player_data


# define teams as class
class Team(object):
    def __init__(self, name, revenue):
        '''
        Initializes a team object
        A team object has the following attributes:
            self.team (str): name of the team
            self.revenue (dbl): budget constraint for team
        '''
        self.name = name
        self.revenue = revenue
