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
      
    # Set the type of the problem
    self._setType()

    # Set total energy at the entrance
    self._setE1()

    # Set total energy at the end
    self._setE2()

    # Set pumb heat
    if self._data['Pu']['h'] == "":
      self._setHp() 

    # Set turbine heat 
    if self._data['Tu']['h'] == "":
      self._setHt() 

    # Set sumatory of accesory K
    self._setSK()

  def _setHp(self):
    """
    Set h of a pumb
    """
    if self._data['Pu']['P'] != '' and self._data['Q'] != '':
      self._data['Pu']['h'] = plib.head(self._data['Pu']['ef'], self._data['Q'], self._data['Pu']['P'], self._g, self._data['rho']) 
    else:
      self._data['Pu']['h'] = 0.

  def _setHt(self):
    """
    Set h of a turbine
    """
    if self._data['Tu']['P'] != '' and self._data['Q'] != '':
      self._data['Tu']['h'] = -1.*plib.head(self._data['Tu']['ef'], self._data['Q'], self._data['Tu']['P'], self._g, self._data['rho']) 
    else:
      self._data['Tu']['h'] = 0.
  
  def _setE1(self):
    """
    Estimate the total energy at the entrance section
    """
    self._E1 = self._data['E1']['z'] +  self._data['E1']['p'] + self._data['E1']['v']

  def _setE2(self):
    """
    Estimate the total energy at the end section
    """
    self._E2 = self._data['E2']['z'] +  self._data['E2']['p'] + self._data['E2']['v']

  def _setSK(self):
    """
    Estimate the total of accesory K
    """
    self._SK = sum(self._data['K'])   

  def getData(self):
    """
    Get the input data
    """
    return self._data

  def _setGravity(self):
    """
    Set the gravity constant
    """
    self._g = plib.gravity(self._data['US'])

  def getGravity(self):
    """
    Get the gravity constant
    """
    return self._g

  def _setType(self):
    """
    Set the type of problem
    """
    if self._data['Q'] == '' and self._data['D'] != '':
      self._typec=1
    elif self._data['Pu']['P'] == '' and self._data['D'] != '':
      self._typec=2
    elif self._data['D'] == '' and self._data['Q'] != '':
      self._typec=3
    
    return self._typec

class SimplePipes():

  def __init__(self):

    # Set the input data
    self._data = InputData()._data
    self._typec = InputData()._typec
    #self._Ht = InputData()._Ht
    self._E1 = InputData()._E1
    self._E2 = InputData()._E2
    self._SK = InputData()._SK
    self._g = InputData()._g

    # Executing de calculation
    self.procedure()

  def procedure(self):
    if self._typec ==1:
      print('')
      print('Proving the system design')
      print('')
      self.designTest()
    elif self._typec ==2:
      print('')
      print('Estimating system power')
      print('')
      self.systemPower()
    elif self._typec ==3:
      print('')
      print('System design')
      print('')
      self.pipeDesign()
      
  def designTest(self): 
    """
    Estimate de velocity/discharge
    """
    if self._data['IM'] == 'fp':
      self._res = plib.f_fp2(self._g, self._data['ks'], self._data['rho'], self._data['mu'], self._data['D'], self._E1, self._E2, self._data['Pu']['h'], self._data['Tu']['h'], self._data['L'], self._SK)
    elif self._data['IM'] == 'nr': 
      self._res = plib.f_nr2(self._g, self._data['ks'], self._data['rho'], self._data['mu'], self._data['D'], self._E1, self._E2, self._data['Pu']['h'], self._data['Tu']['h'], self._data['L'], self._SK)
   
    # Set variables 
    self._V = self._res['V']
    self._f = self._res['f']
    self._hf = self._res['hfrl'][-1]

    # Estimate accesory losses
    self._het = plib.he(self._g,self._SK,self._V)

    # Discharge estimation
    self._Q =  plib.Qc(self._V, self._data['D']) 

    # Get flow regime
    self._fr = plib.flowRegime(self._data['rho'], self._data['mu'], self._data['D'], self._V)

    # Printing results
    self.printIter_designTest()
    self.print_designTest_results()

  def printIter_designTest(self):
    """
    Print iteration table for design test
    """
    print('   Print iteration table for design test   ')
    #print(pd.DataFrame(self._table, columns = ["hf", "he", "f", "V", "Dhf"]))
    self._table = list(zip(self._res['fl'], self._res['Vl'], self._res['hfrl']))
    print(pd.DataFrame(self._table, columns = ["f","V","hf"]))

  def print_designTest_results(self):
    """
    Print design test results
    """
    if self._data['US']=='IS':
      print("Q = %8.4f m³/s" % self._Q)
      print("V = %8.4f m/s" % self._V)
      print("f = %8.4f" % self._f)
      print("hf = %8.4f m" % self._hf)
      print("he = %8.4f m" % self._het)
      print("Flow regime = %s" % self._fr)
    elif self._data['US']=='ES':
      print("Q = %8.4f ft³/s" % self._Q)
      print("V = %8.4f ft/s" % self._V)
      print("f = %8.4f" % self._f)
      print("hf = %8.4f ft" % self._hf)
      print("he = %8.4f ft" % self._het)
      print("Flow regime = %s" % self._fr)

   
  def systemPower(self):
    """
    Estimate the system power
    """
    
    # Calculate de velocity
    self._V = plib.Vc(self._data['Q'], self._data['D'])
    
    # Estimate he
    self._het = plib.he(self._g, self._SK, self._V)

    # Estimate f
    if self._data['IM'] == 'fp':
      self._fdic = plib.f_fp(self._g, self._data['ks'], self._data['rho'], self._data['mu'], self._data['D'], self._V)
    elif self._data['IM'] == 'nr': 
      self._fdic = plib.f_nr(self._g, self._data['ks'], self._data['rho'], self._data['mu'], self._data['D'], self._V)
    
    # Estimate hf
    self._hf = plib.hf(self._g, self._fdic['f'], self._data['L'], self._data['D'], self._V)

    # Total head energy deliver by a pumb from Bernoulli equation
    self._Ht = plib.HPu(self._E1, self._E2, self._het, self._hf, self._data['Tu']['h'])

    # Nominal system power
    self._P = plib.pot(self._data['US'], self._data['Pu']['ef'], self._data['Q'], self._Ht, self._g, self._data['rho'])
    
    # Get flow regime
    self._fr = plib.flowRegime(self._data['rho'], self._data['mu'], self._data['D'], self._V)

    # Printing results
    self.printIter_systemPower()
    self.print_systemPower_results()


  def printIter_systemPower(self):
    """
    Print iteration table for system power
    """
    print('   Print iteration table for system power   ')
    self._table = list(zip(self._fdic['f_list'], self._fdic['df']))
    print(pd.DataFrame(self._table, columns = ["f","df"]))

  def print_systemPower_results(self):
    """
    Print system power results
    """
    if self._data['US']=='IS':
      print("P = %8.2f W" % self._P)
      print("V = %8.4f m/s" % self._V)
      print("f = %8.6f" % self._fdic['f'])
      print("hf = %8.4f m" % self._hf)
      print("he = %8.4f m" % self._het)
      print("Hp = %8.4f m" % self._Ht)
      print("Flow regime = %s" % self._fr)
    elif self._data['US']=='ES':
      print("P = %8.4f Hp" % self._P)
      print("V = %8.4f ft/s" % self._V)
      print("f = %8.6f" % self._f)
      print("hf = %8.4f ft" % self._hf)
      print("he = %8.4f ft" % self._het)
      print("Hp = %8.4f ft" % self._Ht)
      print("Flow regime = %s" % self._fr)


  def pipeDesign(self):
    """
    Estimation of pipe diameter
    """
     
    # Comertial diameter list in inches
    #CD = [1./8, 1./4, 3./8, 1./2, 3./4, 1., 1.+1./4, 1.+1./2, 2., 2.+1./2, 3., 3.+1./2, 4, 4.+1./2, 5., 6., 8., 10., 12., 14., 16., 18., 20., 24., 28., 32., 36., 40., 42., 44., 48., 52., 56., 60.] 
    #CD = [80.42, 103.42, 152.22, 198.48, 247.09, 293.07]
    CD={'3/4':23.63,'1':30.20,'1 1/4':38.14,'1 1/2':43.68,'2':54.58,'2 1/12':66.07,'3':80.42,'4':103.42,'6':152.22,'8':198.21,'10':247.09,'12':293.07,'14':321.76,'16':367.70,'18':413.66,'20':459.64,'24':551.54}   

    # Loop to find the optimal comertial diameter
    self._table = []
    #for D in CD:
    for self._D, self._data['D'] in CD.items():
      self._data['D'] *= 0.001 
      if self._data['IM'] == 'fp':
        self._res = plib.f_fp2(self._g, self._data['ks'], self._data['rho'], self._data['mu'], self._data['D'], self._E1, self._E2, self._data['Pu']['h'], self._data['Tu']['h'], self._data['L'], self._SK)
      elif self._data['IM'] == 'nr': 
        self._res = plib.f_nr2(self._g, self._data['ks'], self._data['rho'], self._data['mu'], self._data['D'], self._E1, self._E2, self._data['Pu']['h'], self._data['Tu']['h'], self._data['L'], self._SK)
      # Set variables 
      self._V = self._res['V']
      self._f = self._res['f']
      self._hf = self._res['hfrl'][-1]

      # Estimate accesory losses
      self._het = plib.he(self._g,self._SK,self._V)

      # Discharge estimation
      self._Q =  plib.Qc(self._V, self._data['D']) 
      testQ = self._Q >= self._data['Q']
       
      self._table.append([self._data['D']*1000., self._Q, testQ, self._f, self._het, self._hf])
      #if self._Q >= self._data['Q']:
      if testQ:
        break

    # Get flow regime
    self._fr = plib.flowRegime(self._data['rho'], self._data['mu'], self._data['D'], self._V)

    # Printing results
    self.printIter_pipeDesign()
    self.print_pipeDesign_results()


  def printIter_pipeDesign(self):
    """
    Print iteration table for system power
    """
    print('   Print iteration table for pipe design   ')
    print(pd.DataFrame(self._table, columns = ["D(mm)", "Q", "Q>=Qd", "f", "he", "hf"]))

  def print_pipeDesign_results(self):
    """
    Print system power results
    """
    if self._data['US']=='IS':
      print("D = %s pulg" % self._D)
      print("Q = %8.4f m/s" % self._Q)
      print("f = %8.6f" % self._f)
      print("hf = %8.4f m" % self._hf)
      print("he = %8.4f m" % self._het)
      print("Flow regime = %s" % self._fr)
    elif self._data['US']=='ES':
      print("D = %s pulg" % self._DC)
      print("Q = %8.4f ft/s" % self._Q)
      print("f = %8.6f" % self._f)
      print("hf = %8.4f ft" % self._hf)
      print("he = %8.4f ft" % self._het)
      print("Flow regime = %s" % self._fr)













#  def designTest2(self):
#    """
#    Estimate de velocity/discharge
#    """
#    # Main loop
#    self._hf = self._Ht
#    #while abs(diff)<=CONST['error']:
#    self._table=[]
#    while True:
#      # Estimate Vi
#      self._V = vel(self._g, self._data['ks'], self._data['rho'], self._data['mu'], self._data['D'], self._data['L'], self._hf)
#    
#      # Friction factor
#      self._f = f_dw(self._g, self._hf, self._data['L'], self._data['D'], self._V)
#    
#      # Estimate hf2
#      hf2 =hfb(self._g, self._Ht, self._data['zo'], self._data['K'], self._V)
#    
#      # Estimate he
#      self._het = he(self._g,sum(self._data['K']),self._V)
#    
#      self._diff = hf2-self._hf
#      self._table.append([self._hf, self._het, self._f, self._V, self._diff])
#      if abs(self._diff)<=1.e-5:
#        break
#      self._hf = hf2
#    
#    # Discharge estimation
#    self._Q =  Qc(self._V, self._data['D']) 
#
#    # Printing results
#    self.printIter_designTest()
#    self.print_designTest_results()



    # Suppose diameter (must be commertial and small
#  def CD(i):
#  """
#  Return comertial diameter based on the i.
#  """
#  if i in range(4):
#    return i*1./8
#  elif i in range(4,8):
#    return i*2*1./8
#  elif i in range(9,15):
#    return i*4*1./8
#  elif i == 16:
#    return 6.
#  elif i in range(17,23):
#    return i*16*1./8
#  elif i in range(24,2):

#  def pipeDesign(self):
#    """
#    Estimate of the pipe comercial diameter
#    """
#    
#    # Suppose hf  
#    self._hf = self._Ht
#     
#    # Suppose diameter (must be commertial and small
#    CD = [1./8, 1./4, 3./8, 1./2, 3./4, 1., 1.+1./4, 1.+1./2, 2., 2.+1./2, 3., 3.+1./2, 4, 4.+1./2, 5., 6., 8., 10., 12., 14., 16., 18., 20., 24., 28., 32., 36., 40., 42., 44., 48., 52., 56., 60.] 
#    self._data['D'] = CD[0]
#
#    i = 1
#    while True:
#      # Estimate V
#      self._V = vel(self._g, self._data['ks'], self._data['rho'], self._data['mu'], self._data['D'], self._data['L'], self._hf)
#    
#      # Estimate Q
#      self._Q =  Qc(self._V, self._D) 
#
#      if self._Q >= self._data['Q']:
#        while True:
#          # Estimate hf2
#          hf2 =hfb(self._g, self._Ht, self._data['zo'], self._data['K'], self._V)
#
#          if abs(hf2-self._hf)<=1.e-5:
#            break
#          else:
#            # Estimate V
#            self._V = vel(self._g, self._data['ks'], self._data['rho'], self._data['mu'], self._data['D'], self._data['L'], self._hf)
#
#      else:
#        self._data['D'] = CD[i]
#        i+=1
#    
#    # Estimate Q
#    self._Q =  Qc(self._V, self._D) 
    
   

#if __name__ == '__main__':
  
