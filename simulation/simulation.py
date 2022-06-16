from classes import *

# initialise the player pool
P = PlayerPool()

# initialise the league
N = League()

# solve skill maximization problem for each team
N.select_optimal_players(P)

# remove all selected players from the pool
P.update_player_pool_after_maximization(N.optimalPlayersSet)

# resolve conflict of player assignment
N.resolve_player_conflicts(P)
