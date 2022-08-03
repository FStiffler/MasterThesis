import imports

# global parameters (do not change during simulation)
alpha = 1.48  # parameter 'alpha' of beta distribution
beta = 3.56  # parameter 'beta' of beta distribution
initialSwissPlayers = 300  # initial number of Swiss players in player pool, references 'k_Swiss,0' in thesis
naturalPlayerBaseGrowth = 0.021  # natural annual growth of swiss player base, references 'kappa' in thesis
leagueSize = 14  # number of teams in the league, references 'n' in thesis
teams = imports.gameAttendanceData['team'].tolist()  # import names of teams, references 'i'
teamSize = 22  # number of players in each team, references 'h' in thesis
playerNumberMin = leagueSize*teamSize  # the number of minimal required players in the player pool, references 'k_min' in thesis
pLambda = 304  # parameter 'lambda' of supply effect
pGamma = 0  # parameter 'gamma' of supply effect
bestPlayerRevenueShare = 0.05  # the share of the best player's salary of the highest team's revenue, references 'gamma' in thesis
marketSize = imports.gameAttendanceData['rsMedian'].tolist()  # per team median of average game attendances in past years, references market size 'm_i' in thesis
seasonPhaseFactor = list(zip([1]*leagueSize, imports.gameAttendanceData['grMedian'].tolist()))  # tuple of season phase factors per team where the first factor is the regular season factor and the second the playoffs factor, references season phase factor 'r_ig' in thesis
initialTeamBudget = [16700000, 6500000, 11000000, 15000000, 15000000, 15000000, 8300000, 8000000, 7100000, 14000000, 12800000, 18400000, 8600000, 10400000]  # create initial team budgets, references 'R_tot_i0'
averageGameRevenues = imports.monetaryFactorData['avgGameRevenue_t-1']  # average home game revenues in season before initial team budgets, references 'R_bar_hat' in thesis
averageWinPer = imports.monetaryFactorData['avgWinningPercentage_t-1']  # average winning percentage season before initial team budgets, references 'omega_bar' in thesis
optimalWinPer = 0.67  # optimal winning percentage, references 'omega_star'
compBalanceEffect = [marketSize[team]/optimalWinPer for team in range(len(teams))]  # per team effect of competitive balance on revenue, references 'b_i' in thesis
monetaryFactor = [averageGameRevenues[team]/(marketSize[team]*averageWinPer[team]-(compBalanceEffect[team]/2)*averageWinPer[team]**2) for team in range(len(teams))]  # calculate monetary factor for each team, references 'z_i' in thesis
initialBroadcastingRevenue = 1450000  # the initial revenue teams receive from broadcasting rights, references 'B' in thesis
broadcastingRevenueGrowth = 0.031  # factor by which the revenue of teams from broadcasting rights grows, references 'pi' in thesis
regularSeason = 0  # parameter indicating regular season
prePlayoff = 1  # parameter indicating prePlayoffs which means best of five series
playoffs = 2  # parameter indicating Playoffs which means best of seven series
