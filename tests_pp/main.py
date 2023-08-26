#!/usr/bin/python3

# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from phydraulics.ppclass import *

def main():

  # Class tha execute de calculus for serial pipes
  ParallelPipes()


if __name__ == '__main__':
  
  main()  


