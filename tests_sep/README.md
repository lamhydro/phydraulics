# `tests_sep`

This directory contain the following:

- `main.py`: This is the python script that call the class `SerialPipes` in `/phydraulics/sepclass.py` which solves the problem.

- `.json` : *JSON* is a friendly format to introduce information to scripts. Note that are multiple files with the  extension `.json`, these files contain information for various types of examples:

  - `designTest.json`: Contain example information to estimate the discharges (Q) in serial pipe.
  - `systemPower.json`: Contain example information to estimate the system power (P) in serial pipes.
  - `pipeDesign.json`: Contain example information to estimate the comercial diameters (D) of serial pipes.

  All the `.json` contain the same structure and information. The structure of a `.json` files is:

   `"PT"`:
    Problem type to be solve. `"PT"` can take the following values : 1 (design test), 2 (system power) and 3 (system design).

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

   `"E1"`:
    Python data estructure call *dictionary*. This contains information related to flow energy at section 1 (entrance) acording to Bernoulli energy equation: `"z"` is the potential energy head, `"p"` is the preassure energy head and `"v"` is the kinematic energy head. If any of them are not given, it must be set equal to 0. The total energy at section 1 is calculated internally. The three data are  given in  `"IS"` or `"BG"`. [*mandatory*] 

   `"E2"`:
    Python data estructure call *dictionary*. This contains information related to flow energy at section 2 (end) acording to Bernoulli energy equation: `"z"` is the potential energy head, `"p"` is the preassure energy head and `"v"` is the kinematic energy head. If any of them are not given, it must be set equal to 0. The total energy at section 2 is calculated internally. The three data are  given in  `"IS"` or `"BG"`. [*mandatory*] 

   `"Ki"`:
    Energy loss coefficient at the system entrance.

   `"Ko"`:
    Energy loss coefficient at the system output.

    For each pipe `"Pi"` in the system, where `i=1...n` and `n` is the number of pipes connected in serie, introduce the following:

    `"Qo"`:
     Flow discharge leaving `"Pi"` at the end of it.

    `"Qi"`:
     Flow discharge transporte by `"Pi"`.

    `"Pu"`:
     Python data estructure call *dictionary*. This contains information related to a pumb: `"P"` is the pump power, `"h"` is the pump head and `"ef"` is the pump eficiency. If neither `"P"` nor `"h"` are given they are set egual to `""`. `"ef"` is egual to 1 if no value is given. If `"P"` is given, the software estimates `"h"` internally. If `"P"` is not given and `"Q"` and `"D"` were given, this means you need to solve problem **type 2** (`systemPower.json`). The three data are  given in  `"IS"` or `"BG"`. [*mandatory*] 

    `"Tu"`:
     Python data estructure call *dictionary*. This contains information related to a turbine: `"P"` is the turbine power, `"h"` is the turbine head and `"ef"` is the turbine eficiency. If neither `"P"` nor `"h"` are given they are set egual to `""`. `"ef"` is egual to 1 if no value is given. If `"P"` is given, the software estimates `"h"` internally and set it negative. The three data are  given in  `"IS"` or `"BG"`. [*mandatory*] 

    `"D"`:
     Real pipe diameter. It is given in  `"IS"` or `"BG"`. It is not given for problem **type 3** (`pipeDesign.json`).

    `"L"`:
     Pipe length. It is given in  `"IS"` or `"BG"`. [*mandatory*] 

    `"ks"`:
     Roughtness of the pipe material. It is given in  `"IS"` or `"BG"`. [*mandatory*]

    `"K"`:
     List of accesory loss coefficients. The software add them up internally. [*mandatory*] 

