# `tests_sp`

This directory contains the following:

- `main.py`: This is the python script that call the class `PorousPipes` in `/phydraulics/popclass.py` which solves the problem.

- `.json` : *JSON* is a friendly format to introduce information to scripts. Note that are multiple files with the  extension `.json`, these files contain information for examples related to energy losses in porous pipes `energyLosses_*.json`.


  All the `.json` contain the same structure and information. The structure of `.json` files are:

   `"US"`:
    Unit measure system. It can be egual to `"IS"` (International system) or  `"ES"` (English system). [*mandatory*]

   `"IM"`:
    Iteration method to resolve the Colebrook-White equation for **f**. It can be egual to `"fp"` (fixed point) or  `"nr"` (Newton-Raphson numerical method). [*mandatory*]

   `"EL"`:
    Method to estimate the energy losses. It can be equal to `"CF"` (Constant friction factor) o `"VF"` (Variable friction factor). [*mandatory*]
    
   `"ks"`:
    Roughtness of the pipe material. It is given in  `"IS"` or `"ES"`. [*mandatory*]

   `"rho"`:
    Fluid density. It is given in  `"IS"` or `"ES"`. [*mandatory*]

   `"mu"`:
    Fluid dynamic viscosity. It is given in  `"IS"` or `"ES"`. If this one is not given (equal `""`), it is estimated based on the  `"rho"` and `"nu"`.

   `"nu"`:
    Fluid dynamic viscosity. It is given in  `"IS"` or `"ES"`. 

   `"q"`:
    Flow discharge per unit length. It is given in  `"IS"` or `"ES"`. [*mandatory*]

   `"D"`:
    Pipe diameter. It is given in  `"IS"` or `"ES"`. [*mandatory*]

   `"L"`:
    Pipe length. It is given in  `"IS"` or `"ES"`. [*mandatory*] 

   `"tl"`:
    Section length. It is given in  `"IS"` or `"ES"`. It is mandatory when `"EL":"VF"`.

