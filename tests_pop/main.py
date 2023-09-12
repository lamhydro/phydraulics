#!/usr/bin/python3

# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from phydraulics.popclass import *

def main():

  # Class that execute the estimation of energy losses for porous pipes
  PorousPipes()


if __name__ == '__main__':
  
  main()  


