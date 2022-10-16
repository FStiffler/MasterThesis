# Introduction

This is the official repository of my master thesis with the title:<br>
*A simulation of the Swiss National League: How the introduction of a salary cap
and the allowance of more import players affect league outcomes*

The master thesis introduces a model to simulate the top tier Swiss ice hockey league,
the National League, in order to measure outcomes when a salary cap or/and more import players
are introduced in the league.

Especially the final simulation code might be of special interest for other, similar
research which is why this repo is public. It provides the following content:

- Latex files to compile the master thesis. Gives the reader an good understanding of final model.
- R files to perform data analysis and creating results used in master thesis and simulation
- Python files to run a simulation of the National League on which the thesis is based

In the following, the content of the simulation in particular is laid out in more detail.

## Simulation

### Files

The simulation consists of a total of seven files located in folder
[simulation](simulation). The files are introduced below:

**[requirements.txt](simulation/requirements.txt):**

Contains the required libraries

**[imports.py](simulation/imports.py):**

Imports data resulting from data analysis required in the simulation.

**[parameters.py](simulation/parameters.py):**

Defines all fixed and initial simulation parameters. They are not meant to be
changed manually except there is evidence suggesting otherwise.

**[classes.py](simulation/classes.py):**

Defines the relevant simulation classes with methods according to the introduced
model in the master thesis.

**[functions.py](simulation/functions.py):**

Introduces functions to run the simulation according to the defined model.

**[simulationModuls.py](simulation/simulationModuls.py):**

Contains the basic elements of the simulation to be integrated.

**[simulation.py](simulation/simulation.py):**

Is the top level file based on which the whole simulation can be configured and
executed. Allows user to define the parameters

- **allowedImports** -> int, Number of allowed import players in the League
- **salaryCap** -> bool, True if simulation to be executed with salary cap, False otherwise
- **seasons** -> int, Number of consecutive seasons to be simulated in one iteration
- **simulationNumber** -> int, Number of simulation iterations to be simulated in one simulation


### Execution

To run a simulation:

1. Install the required libraries defined in [requirements.txt](simulation/requirements.txt)
2. Open [simulation.py](simulation/simulation.py) and define simulation parameters
3. Execute file
4. Have a look at the [results](simulation/results)
