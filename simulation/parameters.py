import imports

# global parameters (do not change during simulation)
alpha = 1.48  # parameter 'alpha' of beta distribution
beta = 3.56  # parameter 'beta' of beta distribution
initialPlayerPoolSize = 342  # initial size of player pool at beginning of simulation, references 'k_0' in thesis
naturalPlayerPoolGrowth = 0.021  # natural annual growth of player pool size (without changes at player limit)
leagueSize = 14  # number of teams in the league, references 'n' in thesis
teams = imports.gameAttendanceData['team'].tolist()  # import names of teams, references 'i'
teamSize = 22  # number of players in each team, references 'h' in thesis
bestPlayerRevenueShare = 0.05  # the share of the best player's salary of the highest team's revenue, references 'gamma' in thesis
monetaryFactor = 100  # monetary factor to be multiplied with every game revenue, references 'M' in thesis
marketSize = imports.gameAttendanceData['rsMedian'].tolist()  # per team median of average game attendances in past years, references market size 'm_i' in thesis
seasonPhaseFactor = list(zip([1]*leagueSize, imports.gameAttendanceData['grMedian'].tolist()))  # tuple of season phase factors per team where the first factor is the regular season factor and the second the playoffs factor, references season phase factor 'r_ig' in thesis
optimalWinPer = 0.67  # optimal winning percentage, references 'omega_star'
compBalanceEffect = [marketSize[team]/optimalWinPer for team in range(len(teams))]  # per team effect of competitive balance on revenue, references 'b_i' in thesis
initialBroadcastingRevenue = 1450000  # the initial revenue teams receive from broadcasting rights, references 'B' in thesis
broadcastingRevenueGrowth = 0.031  # factor by which the revenue of teams from broadcasting rights grows, references 'f' in thesis
regularSeason = 0  # parameter indicating regular season
prePlayoff = 1  # parameter indicating prePlayoffs which means best of five series
playoffs = 2  # parameter indicating Playoffs which means best of seven series
