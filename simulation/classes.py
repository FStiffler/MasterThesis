from parameters import *
import numpy as np


# define player pool as class
class PlayerPool(object):
    def __init__(self, size=k_new):
        '''
        Initializes the player pool object
        size (int): Integer defining the number of players in the pool, default = k_new
        A player pool object has the following attributes:
            self.size (int): determined by size
            self.playerID (numpy array): determines the ID's of players
            self.playerSkill (numpy array): determines the skill level of players
        '''
        self.size = size
        self.playerID = np.arange(1, k_new+1)
        self.playerSkill = np.random.beta(alpha, beta, self.size)
