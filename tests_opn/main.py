#!/usr/bin/python3

# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from phydraulics.opnclass import *

def main():

  # Class to execute the computations for open pipe network
  OpenPipeNet()


if __name__ == '__main__':
  
  main()  


