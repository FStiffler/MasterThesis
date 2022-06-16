from classes import *

# initialise the player pool
playerPool = PlayerPool()

# initialise teams
for i in range(len(teams)):  # for each team
    globals()[teams[i]] = Team(teams[i], revenues[i])  # create a new object of class Team with team name and revenue

# each team selects players
for team in teams:
    print(team)
    eval(team).select_players(playerPool)



