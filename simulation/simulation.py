import os
import simulationModules

# simulation parameters
allowedImports = 10  # the number of allowed import players per team, references 'rho' in thesis
salaryCap = True  # boolean indicator if salary cap is to be simulated or not, references 'R_cap' in thesis
seasons = 10  # the number of consecutive seasons to simulate in one simulation, references 't' in thesis
simulationNumber = 1000  # the number of times the simulation shall be repeated

# run simulation with defined parameters to obtain results on teams and player salaries
combinedSimulationTeamResults, combinedSimulationPlayerResults = simulationModules.simulation(allowedImports, salaryCap, seasons, simulationNumber)

# define file name to save results
playerFileName = "results/playerResults_imports={}_cap={}_seasons={}_simNumb={}.csv".format(allowedImports, salaryCap, seasons, simulationNumber)
teamFileName = "results/teamResults_imports={}_cap={}_seasons={}_simNumb={}.csv".format(allowedImports, salaryCap, seasons, simulationNumber)

# define directory to store results in
saveDirectory = os.path.join(os.getcwd(), "results")

# if directory does not already exist
if not os.path.exists(saveDirectory):
    # create new directory
    os.mkdir(saveDirectory)

# save results to new directory
combinedSimulationPlayerResults.to_csv(playerFileName, index=False)
combinedSimulationTeamResults.to_csv(teamFileName, index=False)
