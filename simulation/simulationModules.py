import pandas as pd
import classes
import parameters


def simulate_one_season(league, season):
    """
    Description:
    Module to simulate one single season

    Input:
    league (League): A league of object League
    season (int): An integer indicating the season

    Returns:
    seasonResults (data frame): A data frame with all relevant results from the season simulation
    """
    # get maximal budget
    maximalBudget = max(league.get_team_budgets())

    # initialise player pool
    playerPool = classes.PlayerPool(season, maximalBudget)

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

    # add column for season
    seasonResults.insert(loc=0, column='Season', value=[season]*parameters.leagueSize)

    # return seasonResults
    return seasonResults


def simulate_consecutive_seasons(simulationResults, seasons):
    """
    Description:
    Module to simulate consecutive seasons

    Input:
    simulationResults (data frame): data frame containing all the simulation results
    seasons (int): the number of consecutive seasons to simulate

    Returns:
    simulationResults (data frame): data frame containing the updated simulation results
    """
    for season in range(1, seasons+1):
        # if it is the first season
        if season == 1:
            # initialise the league
            league = classes.League()

        # simulate season and get results
        seasonResults = simulate_one_season(league, season)

        # add season result to simulation results
        simulationResults = pd.concat([simulationResults, seasonResults])

        # prepare data for following season
        league.reset_for_new_season()

    # return simulation result
    return simulationResults
