#!/usr/bin/python3

import json
import pandas as pd
import sys

from . import plib

class InputData():
  """
  Class to read de input data and initialize some varibles
  """
  def __init__(self):

    # Read input data
    with open(sys.argv[1]) as f:
      self._data = json.load(f)
    
    # Set gravity
    self._setGravity()

    # Set kinematic viscosity
    if self._data['nu'] != '':
      self._data['mu'] = plib.mu(self._data['rho'],self._data['nu'])
      
  def _setGravity(self):
    """
    Set the gravity constant
    """
    self._g = plib.gravity(self._data['US'])

class PorousPipes():

  def __init__(self):

    # Set the input data
    self._data = InputData()._data
    self._g = InputData()._g

    # Executing de calculation
    self.energyLosses()

     
  def energyLosses(self):
    """
    Estimate the energy losses in a porous pipe
    """
    
    # Estimation of entrance discharge and velocity 
    Q1 = plib.entranceDischarge(self._data['q'], self._data['L'])
    V1 = plib.Vc(Q1, self._data['D'])
    
    # Estimation of the critical discharge and velocity
    Qc = plib.criticalDischarge(self._data['D'],self._data['nu']) 
    Vc = plib.Vc(Qc, self._data['D'])

    # Estimation of the critical lenght
    xc = plib.criticalDistance(Qc, Q1, self._data['L'])

    if self._data['EL'] == 'CF': # Constant friction factor
      print('')
      print('Total energy loss in a porous pipe: Constant friction factor method')
      print('')

      # Energy loss in the turbulent zone
      if self._data['IM'] == 'fp':
        ## Friction factor at the pipe entrance
        fl1 = plib.f_fpT(self._g, self._data['ks'], self._data['rho'], self._data['mu'], self._data['D'], V1)
        ## Friction factor at the critical distance
        fl2 = plib.f_fpT(self._g, self._data['ks'], self._data['rho'], self._data['mu'], self._data['D'], Vc)
      elif self._data['IM'] == 'nr': 
        ## Friction factor at the pipe entrance
        fl1 = plib.f_nrT(self._g, self._data['ks'], self._data['rho'], self._data['mu'], self._data['D'], V1)
        ## Friction factor at the critical distance
        fl2 = plib.f_nrT(self._g, self._data['ks'], self._data['rho'], self._data['mu'], self._data['D'], Vc)

      ## Average of turbulent friction factor 
      ft = (fl1['f'] + fl2['f'])*0.5
      
      ## Energy loss
      hft = plib.hf_porousPipe(self._g, self._data['D'], ft, Q1, self._data['q'], self._data['L']-xc)

      # Energy loss in the laminar zone
      f1 = plib.f_L(self._data['rho'], self._data['mu'], self._data['D'], Vc)
      Qe = plib.dischargeToDistance(self._data['q'], self._data['L'], self._data['L']-plib.DLe)
      Ve = plib.Vc(Qe, self._data['D'])
      f2 = plib.f_L(self._data['rho'], self._data['mu'], self._data['D'], Ve)

      ## Average of turbulent friction factor 
      fl = (f1 + f2)*0.5

      ## Energy loss
      hfl = plib.hf_porousPipe(self._g, self._data['D'], fl, Qc, self._data['q'], xc-plib.DLe)

      # Total energy loss
      hf = hft + hfl

      if self._data['US']=='IS':
        print("f for turbulent section = %8.4f" % ft)
        print("hf for turbulent section = %8.4f m" % hft)
        print("f for laminar section = %8.4f" % fl)
        print("hf for laminar section = %8.4f m" % hfl)
        print("Total energy loss = %8.4f m" % hf)
      elif self._data['US']=='ES':
        print("f for turbulent section = %8.4f" % ft)
        print("hf for turbulent section = %8.4f ft" % hft)
        print("f for laminar section = %8.4f" % fl)
        print("hf for laminar section = %8.4f ft" % hfl)
        print("Total energy loss = %8.4f ft" % hf)

    elif self._data['EL'] == 'VF': # Variable friction factor
      print('')
      print('Total energy loss in a porous pipe: Variable friction factor method')
      print('')

      # Estimation of the number of sections
      tn = int(self._data['L']/self._data['tl'])

      # Loop through each section
      l2l = []
      f1l = []
      f2l = []
      hfil = []
      hf = 0.
      for i in range(tn):
        
        l1 = i*self._data['tl']
        Q1 = plib.dischargeToDistance(self._data['q'], self._data['L'], l1)
        V1 = plib.Vc(Q1, self._data['D'])
        l2 = (i+1)*self._data['tl']
        if l2==self._data['L']:
          l2 = self._data['L']-plib.DLe
        Q2 = plib.dischargeToDistance(self._data['q'], self._data['L'], l2)
        V2 = plib.Vc(Q2, self._data['D'])
        if self._data['IM'] == 'fp':
          ## Friction factor at the section entrance
          fl1 = plib.f_fp(self._g, self._data['ks'], self._data['rho'], self._data['mu'], self._data['D'], V1)
          ## Friction factor at the section end
          fl2 = plib.f_fp(self._g, self._data['ks'], self._data['rho'], self._data['mu'], self._data['D'], V2)
        elif self._data['IM'] == 'nr': 
          ## Friction factor at the section entrance
          fl1 = plib.f_nr(self._g, self._data['ks'], self._data['rho'], self._data['mu'], self._data['D'], V1)
          ## Friction factor at the section end
          fl2 = plib.f_nr(self._g, self._data['ks'], self._data['rho'], self._data['mu'], self._data['D'], V2)
        f1 = fl1['f']
        f2 = fl2['f']
        # Average friction factor
        f = 0.5*(f1+f2)
        # Energy loss
        hfi = plib.hf_porousPipe(self._g, self._data['D'], f, Q1, self._data['q'], self._data['tl'])

        # Saving into lists
        l2l.append(l2)
        f1l.append(f1)
        f2l.append(f2)
        hfil.append(hfi)

        hf += hfi

      print(pd.DataFrame(list(zip(l2l,f1l,f2l,hfil)), columns=['Abscisa','fi', 'fi+1', 'hfi'], index=["{:d}".format(x) for x in range(1,tn+1)]))

      print('')
      if self._data['US']=='IS':
        print("Total energy loss = %8.4f m" % hf)
      elif self._data['US']=='ES':
        print("Total energy loss = %8.4f ft" % hf)
      print('')
