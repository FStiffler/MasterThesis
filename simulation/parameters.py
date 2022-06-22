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

# team parameters
teams = imports.gameAttendanceData['team'].tolist()  # name of teams imported, references i
teamBudgets = np.round(
            np.random.uniform(low=15 * maximalSalary, high=20 * maximalSalary, size=leagueSize)).astype(int)  # create team budgets
marketSize = imports.gameAttendanceData['rsMedian'].tolist()  # per team median of average game attendances in past years, references m_i
playoffFactor = imports.gameAttendanceData['grMedian'].tolist()  # per team median of average attendance growth going into playoffs, references r_ig
