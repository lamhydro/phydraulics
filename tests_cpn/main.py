#!/usr/bin/python3

# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from phydraulics.cpnclass import *

def main():

  # Class to execute the computations for open pipe network
  ClosePipeNet()


if __name__ == '__main__':
  
  main()  


