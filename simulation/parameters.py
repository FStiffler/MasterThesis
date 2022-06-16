# model parameters
h = 22  # team size
n = 14  # number of teams in the league
w_max = 10000  # maximal salary for best available player
k_old = n*h  # player pool size before measures
k_new = n*h  # player pool size after measures
alpha = 5  # parameter alpha of beta distribution
beta = 5  # parameter beta of beta distribution

# list of teams
teams = ["team_"+str(i+1) for i in range(n)]

# list of revenues
revenues = [1400000, 1300000, 1200000, 1100000, 1000000, 900000, 800000,
            700000, 600000, 500000, 400000, 300000, 200000, 100000]