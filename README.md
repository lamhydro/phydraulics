# Simple pipe sytems

## Aim

This a repo to solve the three typical problems in pipe hydraulics:

1. **Type 1**: Revision of a simple pipe design. Here, given all the fluid, pipe and flow characteristics, **we estimate the discharte (Q)**.

2. **Type 2**: Estimation of the power required to transport flow from one side to the other. Here, given all the fluid, pipe and flow characteristics, **we estimate the net power (P)**.

3. **Type 3**: Simple pipe design. Here, given all the fluid, pipe and flow characteristics, **we estimate the comercial diameter (D)**.

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

  All the `.json` contain the same structure and information, so that, the scripts are able to indentify which of the three problems need to be solve. The structure of `.json` files is:

   `"US"`:
    Unit measure system. It can be egual to `"IS"` (International system) or  `"BG"` (English system). [*mandatory*]

   `"IM"`:
    Iteration method to resolve the Colebrook-White equation for **f**. It can be egual to `"fp"` (fixed point) or  `"nr"` (Newton-Raphson numerical method). [*mandatory*]
    
   `"ks"`:
    Roughtness of the pipe material. It is given in  `"IS"` or `"BG"`. [*mandatory*]

   `"rho"`:
    Fluid density. It is given in  `"IS"` or `"BG"`. [*mandatory*]

   `"mu"`:
    Fluid dynamic viscosity. It is given in  `"IS"` or `"BG"`. If this one is not given (equal `""`), it is estimated based on the  `"rho"` and `"nu"`.

   `"nu"`:
    Fluid dynamic viscosity. It is given in  `"IS"` or `"BG"`. 

   `"Q"`:
    Flow discharge. It is given in  `"IS"` or `"BG"`. It is not given for problem **type 1** (`designTest.json`).

   `"Pu"`:
    Python data estructure call *dictionary*. This contains information related to a pumb: `"P"` is the pump power, `"h"` is the pump head and `"ef"` is the pump eficiency. If neither `"P"` nor `"h"` are given they are set egual to `""`. `"ef"` is egual to 1 if no value is given. If `"P"` is given, the software estimates `"h"` internally. If `"P"` is not given and `"Q"` and `"D"` were given, this means you need to solve problem **type 2** (`systemPower.json`). The three data are  given in  `"IS"` or `"BG"`. [*mandatory*] 

   `"Tu"`:
    Python data estructure call *dictionary*. This contains information related to a turbine: `"P"` is the turbine power, `"h"` is the turbine head and `"ef"` is the turbine eficiency. If neither `"P"` nor `"h"` are given they are set egual to `""`. `"ef"` is egual to 1 if no value is given. If `"P"` is given, the software estimates `"h"` internally and set it negative. The three data are  given in  `"IS"` or `"BG"`. [*mandatory*] 

   `"D"`:
    Real pipe diameter. It is given in  `"IS"` or `"BG"`. It is not given for problem **type 3** (`pipeDesign.json`).

   `"E1"`:
    Python data estructure call *dictionary*. This contains information related to flow energy at section 1 (entrance) acording to Bernoulli energy equation: `"z"` is the potential energy head, `"p"` is the preassure energy head and `"v"` is the kinematic energy head. If any of them are not given, it must be set equal to 0. The total energy at section 1 is calculated internally. The three data are  given in  `"IS"` or `"BG"`. [*mandatory*] 

   `"E2"`:
    Python data estructure call *dictionary*. This contains information related to flow energy at section 2 (end) acording to Bernoulli energy equation: `"z"` is the potential energy head, `"p"` is the preassure energy head and `"v"` is the kinematic energy head. If any of them are not given, it must be set equal to 0. The total energy at section 2 is calculated internally. The three data are  given in  `"IS"` or `"BG"`. [*mandatory*] 

   `"L"`:
    Pipe length. It is given in  `"IS"` or `"BG"`. [*mandatory*] 

   `"K"`:
    List of accesory loss coefficients. The software add them up internally. [*mandatory*] 

## How to execute it
1. Clone the repo as

  `git clone git@github.com:lamhydro/simplePipes.git`

2. Go into `simplePipes/test` directory:

  `cd simplePipes/test`

3. Execute the code as (e.g.):

  `./main.py designTest.json`

  Here `main.py` reads the `designTest.json` file and resolve problem **type 1**.
