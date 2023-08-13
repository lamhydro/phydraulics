# Simple pipe sytems

## Aim

This a repo to solve the three typical problems in pipe hydraulics:

1. Revision of a simple pipe design. Here, given all the fluid, pipe and flow characteristics, **we estimate the discharte (Q)**.

2. Estimation of the power required to transport flow from one side to the other. Here, given all the fluid, pipe and flow characteristics, **we estimate the net power (P)**.

3. Simple pipe design. Here, given all the fluid, pipe and flow characteristics, **we estimate the comercial diameter (D)**.

## Structure

### `simplePipes`

This directory contain:

- `splib.py`: This is a python library with functions to calculate multiple variables related to simple pipe systems.

- `spclass.py`: This is a python library with classes to solve any of the three problems in simple pipe systems mentioned defore. Here the class `SimplePipes` call other classes and functions to execute the calculus. 

### `test`

This directory contain the following:

- `main.py`: This is the python script that call the class `SimplePipes` in `/simplePipes/spclass.py` which solves the problem.

- `.json` : *JSON* is a friendly format to introduce information to scripts. Note that are multiple files with the  extension `.json`, these files contain information for various types of examples:

  - `designTest.json`: Contain example information to estimate the discharge (Q) transporte by a simple pipe.
  - `systemPower.json`: Contain example information to estimate the system power (P) in a simple pipe system.
  - `pipeDesign.json`: Contain example information to estimate the comercial diameter (D) of a simple pipe.

  All the `.json contain the same structure and information, so that, the scripts are able to indentify which of the three problems need to be solve. The structure of `.json` files is:

  
    




