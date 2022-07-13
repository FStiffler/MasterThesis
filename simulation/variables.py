import parameters
import numpy as np

# initialise global variables at beginning of simulation (change during simulation)
season = 1
playerPoolSize = round(parameters.initialPlayerPoolSize * (1+parameters.naturalPlayerPoolGrowth))  # new player pool size, references 'k_t' in thesis
teamBudget = parameters.initialTeamBudget  # create variable team budgets, references 'R_tot_it-1'
teamPayroll = [0] * parameters.leagueSize  # create variable team payrolls, references 'sum(W_p * d_p)' in thesis
teamSkill = [0] * parameters.leagueSize  # create variable team skills, references 'S_i' in thesis
teamRevenue = [0] * parameters.leagueSize  # create variable revenue, references 'R_tot_it' in thesis
teamWins = [0] * parameters.leagueSize  # create variable for win count
teamGames = [0] * parameters.leagueSize  # create variable for game count
teamRank = [0] * parameters.leagueSize  # create variable for final regular season rank
eliminatedRS = [0] * parameters.leagueSize  # create binary variable indicating regular season elimination
eliminatedPP = [0] * parameters.leagueSize  # create binary variable indicating pre playoffs elimination
eliminatedPR1 = [0] * parameters.leagueSize  # create binary variable indicating playoffs round 1 elimination
eliminatedPR2 = [0] * parameters.leagueSize  # create binary variable indicating playoffs round 2 elimination
eliminatedPR3 = [0] * parameters.leagueSize  # create binary variable indicating playoffs round 3 elimination
champion = [0] * parameters.leagueSize  # create binary variable indicating league champion
maximalSalary = round(parameters.bestPlayerRevenueShare * max(teamBudget))  # maximal salary for best available player, references 'w_max' in thesis
allPlayers = np.arange(start=1, stop=playerPoolSize + 1)  # create players with numbers from 1 to player pool size to create all players in player pool, references 'p' in thesis
allPlayerSkills = np.round(np.random.beta(a=parameters.alpha, b=parameters.beta, size=playerPoolSize), 2)  # draw skill from beta distribution to create all skill levels of players in player pool, references 'S_p' in thesis
allPlayerSalaries = np.round(maximalSalary * allPlayerSkills * (1 - ((playerPoolSize - parameters.initialPlayerPoolSize) / parameters.initialPlayerPoolSize)))  # calculate player salaries to create all salaries in the player pool, references 'W_p' in thesis
