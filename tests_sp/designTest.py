#!/usr/bin/python3

import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import simplePipes as sp

if __name__ == '__main__':
  # Arguments passed
  print("\n Running :", sys.argv[0])

  print("\n Reading :", sys.argv[1])

  # Read input data
  with open(sys.argv[1]) as f:
     data = json.load(f)
  
  print(data)
  
  # Estimate ks/d
  #ks_d = data['ks']/data['D']
  
  # Sum up the system total energy
  Ht = sum(data['H'])
  print(Ht)
  
  # Choose g
  g = gravity(data['US'])
  
  # Main loop
  hf = Ht
  #while abs(diff)<=CONST['error']:
  table=[]
  while True:
    # Estimate Vi
    Vi = vel(g, data['ks'], data['rho'], data['mu'], data['D'], data['L'], hf)
  
    # Friction factor
    f = f_dw(g, hf,data['L'], data['D'], Vi)
  
    # Estimate hf2
    hf2 =hfb(g, Ht, data['zo'], data['K'], Vi)
  
    # Estimate he
    het = he(g,sum(data['K']),Vi)
  
    diff = hf2-hf
    table.append([hf, het, f, Vi, diff])
    if abs(diff)<=1.e-5:
      break
    hf = hf2
  
  df = pd.DataFrame(table, columns = ["hf", "he", "f", "V", "Dhf"])
  print(df)
  
  
   
