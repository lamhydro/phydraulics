# `tests_onp`

This directory contain the following:

- `main.py`: This is the python script that call the class `OpenPipesNet` in `/phydraulics/opnclass.py` which solves the problem.

- `.json` : *JSON* is a friendly format to introduce information to scripts. Note that are multiple files with the  extension `.json`, these files contain information for various types of examples:

  - `designTest.json`: Contain example information to estimate the discharges (Q) in pipes in parallel.
  - `pipeDesign.json`: Contain example information to estimate the comercial diameters (D) of pipes in parallel.

  All the `.json` contain the same structure and information. The structure of a `.json` files is:

   `"PT"`:
    Problem type to be solve. `"PT"` can take the following values : 1 (design test) and 3 (system design).

   `"US"`:
    Unit measure system. It can be egual to `"IS"` (International system) or  `"BG"` (English system). [*mandatory*]

   `"IM"`:
    Iteration method to resolve the Colebrook-White equation for **f**. It can be egual to `"fp"` (fixed point) or  `"nr"` (Newton-Raphson numerical method). [*mandatory*]

   `"rho"`:
    Fluid density. It is given in  `"IS"` or `"BG"`. [*mandatory*]

   `"mu"`:
    Fluid dynamic viscosity. It is given in  `"IS"` or `"BG"`. If this one is not given (equal `""`), it is estimated based on the  `"rho"` and `"nu"`.

   `"nu"`:
    Fluid dynamic viscosity. It is given in  `"IS"` or `"BG"`. 

    For a reservoir `"Ri"` in the open pipe network, where `i=1...n` and `m` is the number of reservoir, introduce the reservoir altitute (`"z"`) and the reservoir outflow (`"Q"`).

    For a node (intesection of different pipes) `"Ni"` in the open pipe network, where `i=1...s` and `s` is the number of nodes, introduce the node altitute (`"z"`) and the node outflow (`"Q"`).

    For each pipe `"Pi"` in the system, where `i=1...n` and `n` is the number of pipes connected, introduce the following:


   `"S"`:
    Start point for `"Pi"`. Can be a reservoir `"Ri"` or a node `"Ni"`.   

   `"E"`:
    End point for `"Pi"`. Can be a reservoir `"Ri"` or a node `"Ni"`.   

   `"Pu"`:
    Python data estructure call *dictionary*. This contains information related to a pumb: `"P"` is the pump power, `"h"` is the pump head and `"ef"` is the pump eficiency. If neither `"P"` nor `"h"` are given they are set egual to `""`. `"ef"` is egual to 1 if no value is given. If `"P"` is given, the software estimates `"h"` internally. If `"P"` is not given and `"Q"` and `"D"` were given, this means you need to solve problem **type 2** (`systemPower.json`). The three data are  given in  `"IS"` or `"BG"`. [*mandatory*] 

   `"D"`:
    Real pipe diameter. It is given in  `"IS"` or `"BG"`. It is not given for problem **type 3** (`pipeDesign.json`).

   `"L"`:
    Pipe length. It is given in  `"IS"` or `"BG"`. [*mandatory*] 

   `"ks"`:
    Roughtness of the pipe material. It is given in  `"IS"` or `"BG"`. [*mandatory*]

   `"K"`:
    List of accesory loss coefficients. The software add them up internally. [*mandatory*] 
  
