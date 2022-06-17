# model parameters
teamSize = 22  # references 'h' in thesis
leagueSize = 14  # number of teams in the league, references 'n' in thesis
maximalSalary = 100000  # maximal salary for best available player, references 'w_max' in thesis
oldPlayerPoolSize = teamSize*leagueSize  # player pool size before measures, references 'k_old' in thesis
newPlayerPoolSize = teamSize*leagueSize  # player pool size after measures, references 'k_new' in thesis
alpha = 3  # parameter alpha of beta distribution
beta = 3  # parameter beta of beta distribution
