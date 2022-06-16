from classes import *

# initialise the player pool
P = PlayerPool()

# initialise the league
N = League()

# solve skill maximization problem for each team
N.select_optimal_players(P)


