from parameters import *
import numpy as np
import pandas as pd
import pulp as pl
from pulp import PULP_CBC_CMD


# define function to select players and maximizing skill
def skill_maximization(playerPool, budgetConstraint):
    '''
    playerPool (PlayerPool): A player pool of object PlayerPool
    budgetConstraint (dbl): The budget constraint for a particular team used to optimize skill
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
    prob += pl.lpSum(binaries[i] * salaries[i] for i in range(len(players))) <= budgetConstraint  # budget constraint

    # solve problem to obtain the optimal solution (best team)
    prob.solve(solver=PULP_CBC_CMD(msg=False))

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

    # assert that constraints hold since the solver does not throw an error when not converging to a solution
    assert len(selectedPlayers) == h
    assert selectedPlayers.Salary.sum() <= budgetConstraint


    # return selected team
    return selectedPlayers

# function to identify conflicts of player assignment
def identify_conflicts(optimalPlayers, optimalPlayersSet):
    '''
    optimalPlayers (dict): A dictionary which shows the players selected by every team after the maximization process
    derived from an object with class League after calling method select_optimal_players
    optimalPlayersSet (set): A set which shows all players selected by any team during the maximization process
    derived from an object with class League after calling method select_optimal_players
    Returns:
    conflicts (dict): A dictionary showing the conflicting player id as key and all interested teams as values in a list
    noConflicts (dict): A dictionary showing the non-conflicting player id as key and the interested team as value in a list
    '''

    # create a data frame from dictionary
    optimalPlayersDF = pd.DataFrame(optimalPlayers)

    # pivot to long format
    optimalPlayersDF = pd.melt(optimalPlayersDF,
                               value_vars=optimalPlayersDF.columns,
                               var_name='team',
                               value_name='player')

    # initialise empty dictionaries to be filled with observed conflicts and non conflicts
    conflicts = {}
    noConflicts = {}

    # loop over all players to identify conflicts
    for player in optimalPlayersSet:

        # extract all teams interested in the same player
        I = optimalPlayersDF.loc[optimalPlayersDF['player'] == player]

        # if more than one team want to acquire a player
        if len(I) > 1:

            # fill player as key and list of teams in conflicts dictionary
            conflicts[player] = I.team.tolist()

        # if only one team wants to acquire a player
        else:
            noConflicts[player] = I.team.tolist()

    # return dictionaries
    return conflicts, noConflicts

# function to assign a player to a team
def assign_player(finalPlayerSelection, player, team):
    '''
    finalPlayerSelection (dict): A dictionary which shows the final player selection of teams so far
    derived from an object with class League
    player (int): The new player to be added to the already existing selection of players
    team (str): The team to which the new player is to be assigned
    Returns:
    finalPlayerSelection (dict): Updates and returns final player selection
    '''

    # append the new player to a list of existing players for a team
    finalPlayerSelection[team].append(player)

    # return
    return finalPlayerSelection







