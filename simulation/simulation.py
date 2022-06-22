import classes

# initialise the player pool
playerPool = classes.PlayerPool()

# initialise the league
league = classes.League()

# solve skill maximization problem for each team
league.select_optimal_players(playerPool)

# remove all selected players from the pool
playerPool.update_player_pool_after_maximization(league.optimalPlayersSet)

# resolve conflict of player assignment
league.resolve_player_conflicts(playerPool)

# simulate season
league.simulate_season()
