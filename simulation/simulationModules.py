import pandas as pd
import classes
import functions
import parameters


def simulate_one_season(league, allowedImports, salaryCap, season, simulationIteration):
    """
    Description:
    Module to simulate one single season

    Input:
    league (League): A league of object League
    season (int): An integer the number of allowed import players per team
    salaryCap (bool): boolean parameter indicating presence of salary cap
    season (int): An integer indicating the season
    simulationIteration (int): the current simulation iteration

    Returns:
    seasonTeamResults (data frame): A data frame with all relevant team results from the season simulation
    seasonPlayerResults (data frame): A data frame with all relevant player salary results from the season simulation
    """
    # calculate maximal budget
    maximalBudget = functions.calculate_maximal_budget(league, salaryCap)

    # initialise player pools
    print("Player pools are initialised")
    domesticPlayerPool = classes.DomesticPlayerPool(season, maximalBudget, allowedImports)
    foreignPlayerPool = classes.ForeignPlayerPool(season, maximalBudget, allowedImports)

    # solve skill maximization problem for each team on domestic players
    print("Teams solve sub-problem 1: Selection of domestic players")
    league.select_optimal_domestic_players(domesticPlayerPool)

    # remove all selected players from the pool of domestic players
    domesticPlayerPool.update_player_pool_after_maximization(league.optimalDomesticPlayersSet)

    # resolve conflict of domestic player assignment
    print("Teams solve sub-problem 1: Conflicting domestic player selection")
    league.resolve_player_conflicts(domesticPlayerPool)

    # select import players
    print("Teams solve sub-problem 3: Selection of import players")
    league.select_optimal_import_players(foreignPlayerPool, domesticPlayerPool, allowedImports)

    # if a team went bankrupt
    if league.leagueCondition == "bankruptcy":
        # create season results
        seasonTeamResults = league.teamData.iloc[:, :-4]

        # add columns to inform season status to team data
        seasonTeamResults.insert(loc=0, column='validSeason', value=[False] * parameters.leagueSize)
        seasonTeamResults.insert(loc=0, column='season', value=[season] * parameters.leagueSize)

        # combine player data of both player pools for player statistics
        combinedPlayersData = pd.concat([domesticPlayerPool.allPlayersData, foreignPlayerPool.allPlayersData],
                                        ignore_index=True)

        # extract player stats
        seasonPlayerResults = league.get_player_stats(combinedPlayersData)

        # add columns to inform season status to player data
        seasonPlayerResults.insert(loc=0, column='validSeason', value=False)
        seasonPlayerResults.insert(loc=0, column='season', value=season)

        # return seasonResults
        return seasonTeamResults, seasonPlayerResults

    # simulate season
    league.simulate_season()

    # calculate final team revenue
    print("Final revenues are calculated")
    league.calculate_season_revenue(season)

    # create season results
    seasonTeamResults = league.teamData.iloc[:, :-4]

    # add columns to inform season status to team data
    seasonTeamResults.insert(loc=0, column='validSeason', value=[True] * parameters.leagueSize)
    seasonTeamResults.insert(loc=0, column='season', value=[season] * parameters.leagueSize)

    # combine player data of both player pools for player statistics
    combinedPlayersData = pd.concat([domesticPlayerPool.allPlayersData, foreignPlayerPool.allPlayersData],
                                    ignore_index=True)

    # extract player stats
    seasonPlayerResults = league.get_player_stats(combinedPlayersData)

    # add columns to inform season status to player data
    seasonPlayerResults.insert(loc=0, column='validSeason', value=True)
    seasonPlayerResults.insert(loc=0, column='season', value=season)

    # return seasonResults
    return seasonTeamResults, seasonPlayerResults


def simulate_consecutive_seasons(simulationTeamResults, simulationPlayerResults, allowedImports, salaryCap, seasons, simulationIteration, simulationNumber):
    """
    Description:
    Module to simulate consecutive seasons

    Input:
    simulationTeamResults (data frame): data frame containing all the simulation team results
    simulationPlayerResults (data frame): data frame containing all the simulation player results
    allowedImports (int): the number of allowed import players per team
    salaryCap (bool): boolean parameter indicating presence of salary cap
    seasons (int): the number of consecutive seasons to simulate
    simulationNumber (int): the total number of simulations to be conducted

    Returns:
    simulationTeamResults (data frame): data frame containing the updated simulation team results for one simulation
    simulationPlayerResults (data frame): data frame containing the updated simulation player salary results for one simulation
    """
    # for each season in the range of seasons
    for season in range(1, seasons + 1):

        # print season
        print("\n\nSimulation {}/{}, Season {}/{}:\n".format(simulationIteration, simulationNumber, season, seasons))

        # if it is the first season
        if season == 1:
            # initialise the league
            league = classes.League()
            print("One-time initialization of league\n")

        # simulate season and get results
        seasonTeamResults, seasonPlayerResults = simulate_one_season(league, allowedImports, salaryCap, season, simulationIteration)

        # if the simulation came to a break condition
        if not seasonTeamResults['validSeason'][0]:

            # add season team result to simulation results
            simulationTeamResults = pd.concat([simulationTeamResults, seasonTeamResults], ignore_index=True)

            # add season player result to simulation results
            simulationPlayerResults = pd.concat([simulationPlayerResults, seasonPlayerResults], ignore_index=True)

            # add columns to inform simulation status to team data
            simulationTeamResults.insert(loc=0, column='validSimulation', value=[False] * len(simulationTeamResults))
            simulationTeamResults.insert(loc=0, column='simulation', value=[simulationIteration] * len(simulationTeamResults))

            # add columns to inform simulation status to player data
            simulationPlayerResults.insert(loc=0, column='validSimulation', value=[False] * len(simulationPlayerResults))
            simulationPlayerResults.insert(loc=0, column='simulation', value=[simulationIteration] * len(simulationPlayerResults))

            # break simulation
            print("Simulation is terminated and termination condition is noted")
            return simulationTeamResults, simulationPlayerResults

        # add season team result to simulation results
        simulationTeamResults = pd.concat([simulationTeamResults, seasonTeamResults], ignore_index=True)

        # add season player result to simulation results
        simulationPlayerResults = pd.concat([simulationPlayerResults, seasonPlayerResults], ignore_index=True)

        # prepare data for following season
        print("League is reset for next season simulation")
        league.reset_for_new_season()

    # add columns to inform simulation status to team data
    simulationTeamResults.insert(loc=0, column='validSimulation', value=[True] * len(simulationTeamResults))
    simulationTeamResults.insert(loc=0, column='simulation', value=[simulationIteration] * len(simulationTeamResults))

    # add columns to inform simulation status to player data
    simulationPlayerResults.insert(loc=0, column='validSimulation', value=[True] * len(simulationPlayerResults))
    simulationPlayerResults.insert(loc=0, column='simulation', value=[simulationIteration] * len(simulationPlayerResults))

    # return simulation result
    return simulationTeamResults, simulationPlayerResults


def simulation(allowedImports, salaryCap, seasons, simulationNumber):
    """
    Description:
    Module to conduct a simulation given the input parameters

    Input:
    allowedImports (int): the number of allowed import players per team
    salaryCap (bool): boolean parameter indicating presence of salary cap, True = present
    seasons (int): the number of consecutive seasons to simulate
    simulationNumber (int): the number of times the simulation shall be repeated

    Returns:
    combinedSimulationTeamResults (data frame): data frame containing the updated simulation team results for all simulations
    combinedSimulationPlayerResults (data frame): data frame containing the updated simulation player salary results for all simulations
    """
    # initialize empty data frames to log results of all simulations
    combinedSimulationTeamResults = pd.DataFrame()
    combinedSimulationPlayerResults = pd.DataFrame()

    # initialize simulation iterable
    simulationIteration = 1

    # while the total number of simulations is not reached
    while simulationIteration <= simulationNumber:

        # print information simulation
        print("\nStart of simulation {} of {}".format(simulationIteration, simulationNumber))

        # initialize empty data frames to log results of one simulation
        simulationTeamResults = pd.DataFrame()
        simulationPlayerResults = pd.DataFrame()

        # run one simulation of defined consecutive seasons
        simulationTeamResults, simulationPlayerResults = simulate_consecutive_seasons(simulationTeamResults, simulationPlayerResults, allowedImports, salaryCap, seasons, simulationIteration, simulationNumber)

        # add simulation team result to combined simulation results
        combinedSimulationTeamResults = pd.concat([combinedSimulationTeamResults, simulationTeamResults], ignore_index=True)

        # add simulation player result to combined simulation results
        combinedSimulationPlayerResults = pd.concat([combinedSimulationPlayerResults, simulationPlayerResults], ignore_index=True)

        # print information to indicate end of simulation
        print("\nEnd of simulation {} of {}\n\n".format(simulationIteration, simulationNumber))

        # increase simulation iterable
        simulationIteration += 1

    # return simulation result
    return combinedSimulationTeamResults, combinedSimulationPlayerResults