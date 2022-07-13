import pandas as pd


def simulate_one_season(playerPool, league, season):
    """
    Description:
    Module to simulate one single season

    Input:
    playerPool (PlayerPool): A player pool of object PlayerPool
    league (League): A league of object League
    season (int): An integer indicating the season

    Returns:
    seasonResults (data frame): A data frame with all relevant results from the season simulation
    """
    # solve skill maximization problem for each team
    league.select_optimal_players(playerPool)

    # remove all selected players from the pool
    playerPool.update_player_pool_after_maximization(league.optimalPlayersSet)

    # resolve conflict of player assignment
    league.resolve_player_conflicts(playerPool)

    # simulate season
    league.simulate_season()

    # calculate final team revenue
    league.calculate_season_revenue(season)

    # create season results
    seasonResults = league.teamData.iloc[:, :-4]

    # return seasonResults
    return seasonResults


def simulate_consecutive_seasons(simulationResults):
    """
    Description:
    Module to simulate consecutive seasons

    Input:
    simulationResults

    Returns:

    """
    import classes
    import variables

    # initialise the player pool
    playerPool = classes.PlayerPool()

    # initialise the league
    league = classes.League()

    # initialise season
    season = variables.season

    # simulate season and get results
    seasonResults = simulate_one_season(playerPool, league, season)

    # add season result to simulation results
    simulationResults = pd.concat([simulationResults, seasonResults])

    # return simulation result
    return simulationResults
