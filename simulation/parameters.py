import numpy as np
import imports

# global parameters
teamSize = 22  # references 'h' in thesis
leagueSize = 14  # number of teams in the league, references 'n' in thesis
maximalSalary = 100000  # maximal salary for best available player, references 'w_max' in thesis
oldPlayerPoolSize = 500  # player pool size before measures, references 'k_old' in thesis
newPlayerPoolSize = 500  # player pool size after measures, references 'k_new' in thesis
alpha = 3  # parameter alpha of beta distribution
beta = 3  # parameter beta of beta distribution
prePlayoff = 1  # parameter indicating prePlayoffs which means best of five series
playoffs = 2  # parameter indicating Playoffs which means best of seven series
monetaryFactor = 2  # monetary factor to be multiplied with every game revenue, references M in thesis
optimalWinPer = 0.6  # optimal winning percentage, references omega_star

# player parameters
allPlayers = np.arange(start=1, stop=newPlayerPoolSize + 1)  # create id's from 1 to newPlayerPoolSize, all players in player pool, references p in thesis
allPlayerSkills = np.round(np.random.beta(a=alpha, b=beta, size=newPlayerPoolSize), 2)  # draw skill from beta distribution, all skill levels of players in player pool, references S_p in thesis
allPlayerSalaries = np.round(maximalSalary * allPlayerSkills * (1 - ((newPlayerPoolSize - oldPlayerPoolSize) / oldPlayerPoolSize)))  # calculate player salaries, all salaries in the player pool, references W_p in thesis

# team parameters
teams = imports.gameAttendanceData['team'].tolist()  # name of teams imported, references i
teamBudgets = np.round(
            np.random.uniform(low=15 * maximalSalary, high=20 * maximalSalary, size=leagueSize)).astype(int)  # create team budgets
marketSize = imports.gameAttendanceData['rsMedian'].tolist()  # per team median of average game attendances in past years, references m_i in thesis
playoffFactor = imports.gameAttendanceData['grMedian'].tolist()  # per team median of average attendance growth going into playoffs, references r_ig in thesis
compBalanceEffect = [marketSize[team]/optimalWinPer for team in range(len(teams))]
