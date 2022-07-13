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
    seasonTeamResults (data frame): A data frame with all relevant team results from the season simulation
    seasonPlayerResults (data frame): A data frame with all relevant player results from the season simulation
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
    seasonTeamResults = league.teamData.iloc[:, :-4]

    # add column for season
    seasonTeamResults.insert(loc=0, column='Season', value=[season]*parameters.leagueSize)

    # extract player stats
    seasonPlayerResults = playerPool.get_player_stats()

    # add column for season
    seasonPlayerResults.insert(loc=0, column='Season', value=season)

    # return seasonResults
    return seasonTeamResults, seasonPlayerResults


def simulate_consecutive_seasons(simulationTeamResults, simulationPlayerResults, seasons):
    """
    Description:
    Module to simulate consecutive seasons

    Input:
    simulationTeamResults (data frame): data frame containing all the simulation team results
    simulationPlayerResults (data frame): data frame containing all the simulation player results
    seasons (int): the number of consecutive seasons to simulate

    Returns:
    simulationTeamResults (data frame): data frame containing the updated simulation team results
    simulationPlayerResults (data frame): data frame containing the updated simulation player results
    """
    for season in range(1, seasons+1):
        # if it is the first season
        if season == 1:
            # initialise the league
            league = classes.League()

        # simulate season and get results
        seasonTeamResults, seasonPlayerResults = simulate_one_season(league, season)

        # add season team result to simulation results
        simulationTeamResults = pd.concat([simulationTeamResults, seasonTeamResults], ignore_index=True)

        # add season player result to simulation results
        simulationPlayerResults = pd.concat([simulationPlayerResults, seasonPlayerResults], ignore_index=True)

        # prepare data for following season
        league.reset_for_new_season()

    # return simulation result
    return simulationTeamResults, simulationPlayerResults
