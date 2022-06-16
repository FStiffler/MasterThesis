from parameters import *
import numpy as np
import pandas as pd
import pulp as pl
from pulp import PULP_CBC_CMD


# define function to select players
def select_players(playerPool):
    '''
    playerPool (PlayerPool): A player pool of object PlayerPool
    Returns:
    selectedPlayers (pandas dataframe): A pandas dataframe which includes data about selected players
    '''

    # initialize variables
    playerData = playerPool.get_data()  # get player data in a data frame
    players = playerPool.get_player_id()  # get players ID's in a list list
    skills = playerPool.get_player_skill()  # get player skill in a list
    salaries = playerPool.get_player_salary()  # get player salaries in a list
    binaries = [pl.LpVariable(  # initialise list of binary variables, one for each player
        "d_" + str(players[i]),  # name the variables: d_playerID
        cat="Binary") for i in range(len(players))]  # iterate through all players

    # initialize problem
    prob = pl.LpProblem(name="BestTeam", sense=-1)  # sense=-1 indicates maximization problem

    # define objective function
    prob += pl.lpSum(binaries[i] * skills[i] for i in range(len(players)))  # maximize skill

    # define the constraints
    prob += pl.lpSum(binaries[i] for i in range(len(players))) == h  # team size constraint
    prob += pl.lpSum(binaries[i] * salaries[i] for i in range(len(players))) <= R_tot_i  # budget constraint

    # solve problem to obtain the optimal solution (best team)
    prob.solve()

    # initialize empty lists for the variable names and solution values
    variables = []
    solutions = []

    # write each variable name and solution value to the lists
    for v in prob.variables():
        variable = v.name
        solution = v.varValue
        variables.append(variable)  # append variable name to existing list
        solutions.append(solution)  # append solution value to existing list

    # obtain selected players
    solutions = np.array(solutions).astype(int)  # define solution values as integers (binary)
    solutionDF = pd.DataFrame(  # define a data frame with all variables and according optimal values
        data=np.array([variables, solutions]).T,  # .T makes sure to convert the 2xn matrix to a nx2 matrix
        columns=['Variable', 'Optimal Value']
    )
    solutionDF['Optimal Value'] = solutionDF['Optimal Value'].astype(int)  # define column as binary
    solutionDF = solutionDF[solutionDF['Optimal Value'] == 1]  # filter selected players
    selectedPlayers = playerData.loc[  # create data frame with information about selected players
        playerData['ID'].isin(  # filter ID's in array
            np.array(
                solutionDF.Variable.str.split('_').tolist()  # extract player ID from variable name
            )[:, 1].astype(int)  # select only ID numbers and define them as integer
        )
    ]



    # return selected team
    return selectedPlayers