# Pipe Hydraulics 

## Aim

This a repo to solve the three typical problems for **permanent flow** in pipe hydraulics:

1. **Type 1**: Revision of a simple pipe design. Here, given all the fluid, pipe and flow characteristics, **we estimate the discharte (Q)**.

2. **Type 2**: Estimation of the power required to transport flow from one side to the other. Here, given all the fluid, pipe and flow characteristics, **we estimate the net power (P)**.

3. **Type 3**: Simple pipe design. Here, given all the fluid, pipe and flow characteristics, **we estimate the comercial diameter (D)**.

for the folling pipe system:

1. **Simple pipes**: This a system of one pipe where the geometry and its physical characteristics are constant.

2. **Serial pipes**: This system is made up by diferent pipes conected one after one. The geometrical and physical characteristics are diferent for each pipe. There are outflows at the end of each pipe. 

3. **Parallel pipes**: This system is composed for usually 2 or seldom more pipes conected in parallel between two nodes. The geometrical and physical characteristics are usually diferent for each pipe.

4. **Open pipe network**: This is a system of reservoir conected by pipes and nodes. Usually, there is a reservoir that supply to downstream reservoir throuthg the pipes. Sometimes there are outflow at the nodes. 

## Structure

### `phydraulics`

This directory contains:

- `plib.py`: This is a python library with functions to calculate multiple variables related to pipe systems.

- `spclass.py`: This is a python library with classes to solve any of the three problems in **simple pipe** systems mentioned defore. Here the class `SimplePipes` call other classes and functions to execute the calculus. 

- `sepclass.py`: This is a python library with classes to solve any of the three problems in **serial pipe systems** mentioned defore. Here the class `SerialPipes` call other classes and functions to execute the calculus. 

- `ppclass.py`: This is a python library with classes to solve any of the three problems in **parallel pipe systems** mentioned defore. Here the class `ParallelPipes` call other classes and functions to execute the calculus. 

- `opnclass.py`: This is a python library with classes to solve problem type 1 and type 2 in **open pipe networks** mentioned defore. Here the class `OpenPipesNet` call other classes and functions to execute the calculus. 


There are some directories named as `test_*`, that have the following structure:

-  [tests_sp](./tests_sp/README.md)

-  [tests_sep](./tests_sep/README.md)

-  [tests_pp](./tests_pp/README.md)

-  [tests_opn](./tests_opn/README.md)


## How to execute it
1. Clone the repo as

  `git clone git@github.com:lamhydro/phydraulics.git`

2. For example, go into `phydraulics/test_sp` (Simple pipes) directory:

  `cd phydraulics/test_sp`

3. Execute the code as (e.g.):

  `./main.py designTest.json`

  Here `main.py` reads the `designTest.json` file and resolve problem **type 1** for simple pipes.
