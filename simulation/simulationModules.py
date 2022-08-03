import pandas as pd
import classes
import parameters


def simulate_one_season(league, allowedImports, season):
    """
    Description:
    Module to simulate one single season

    Input:
    league (League): A league of object League
    season (int): An integer the number of allowed import players per team
    season (int): An integer indicating the season

    Returns:
    seasonTeamResults (data frame): A data frame with all relevant team results from the season simulation
    seasonPlayerResults (data frame): A data frame with all relevant player results from the season simulation
    """
    # get maximal budget
    maximalBudget = max(league.get_team_budgets())

    # initialise player pools
    domesticPlayerPool = classes.DomesticPlayerPool(season, maximalBudget, allowedImports)
    foreignPlayerPool = classes.ForeignPlayerPool(season, maximalBudget, allowedImports)

    # solve skill maximization problem for each team on domestic players
    league.select_optimal_domestic_players(domesticPlayerPool)

    # remove all selected players from the pool of domestic players
    domesticPlayerPool.update_player_pool_after_maximization(league.optimalDomesticPlayersSet)

    # resolve conflict of domestic player assignment
    league.resolve_player_conflicts(domesticPlayerPool)

    # select import players
    league.select_optimal_import_players(foreignPlayerPool, domesticPlayerPool, allowedImports)

    # simulate season
    league.simulate_season()

    # calculate final team revenue
    league.calculate_season_revenue(season)

    # create season results
    seasonTeamResults = league.teamData.iloc[:, :-4]

    # add column for season
    seasonTeamResults.insert(loc=0, column='Season', value=[season]*parameters.leagueSize)

    # combine player data of both player pools for player statistics
    combinedPlayersData = pd.concat([domesticPlayerPool.allPlayersData, foreignPlayerPool.allPlayersData], ignore_index=True)

    # extract player stats
    seasonPlayerResults = league.get_player_stats(combinedPlayersData)

    # add column for season
    seasonPlayerResults.insert(loc=0, column='Season', value=season)

    # return seasonResults
    return seasonTeamResults, seasonPlayerResults


def simulate_consecutive_seasons(simulationTeamResults, simulationPlayerResults, allowedImports, seasons):
    """
    Description:
    Module to simulate consecutive seasons

    Input:
    simulationTeamResults (data frame): data frame containing all the simulation team results
    simulationPlayerResults (data frame): data frame containing all the simulation player results
    allowedImports (int): the number of allowed import players per team
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
        seasonTeamResults, seasonPlayerResults = simulate_one_season(league, allowedImports, season)

        # add season team result to simulation results
        simulationTeamResults = pd.concat([simulationTeamResults, seasonTeamResults], ignore_index=True)

        # add season player result to simulation results
        simulationPlayerResults = pd.concat([simulationPlayerResults, seasonPlayerResults], ignore_index=True)

        # prepare data for following season
        league.reset_for_new_season()

    # return simulation result
    return simulationTeamResults, simulationPlayerResults
