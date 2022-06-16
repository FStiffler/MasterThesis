from functions import select_players
from classes import *

# initialise the player pool
playerPool = PlayerPool()

# initialise teams
for i in range(len(teams)):
    globals()[teams[i]] = Team(teams[i], revenues[i])

# select players
selectedPlayers = select_players(playerPool)
