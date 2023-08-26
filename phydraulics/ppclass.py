#!/usr/bin/python3

import json
import pandas as pd
import sys
import math

from . import plib

class InputData():
  """
  Class to read de input data and initialize some varibles
  """
  def __init__(self):

    # Read input data
    with open(sys.argv[1]) as f:
      self._data = json.load(f)
    
    # Count the number of pipes
    self._getNpipes()

    # Set gravity
    self._setGravity()

    # Set kinematic viscosity
    if self._data['nu'] != '':
      self._data['mu'] = plib.mu(self._data['rho'],self._data['nu'])
      
    # Set total energy at the entrance
    self._setE1()

    # Set total energy at the end
    self._setE2()

    # Set pipe relation of Dz/Lt
    self._setPrel()

    # Set pumb heat
    self._setHp() 

    # Set turbine heat 
    self._setHt() 

    # Set sumatory of accesory K
    self._setSK()


  def _setPrel(self):
    """
    Set pipe relation of Dz/Lt (Lt: total pipe lenght)
    """
    # Total length of pipes
    self._rel = [0]*self._npipes
    Dz = abs(self._data['E1']['z'] - self._data['E2']['z'])
    for i in range(1,self._npipes+1): 
      self._rel[i-1] = Dz/self._data['P'+str(i)]['L']

  def _getNpipes(self):
    """
    Count the number of pipes
    """
    self._npipes = 0
    for i in range(len(self._data)):
      for key in self._data:
        if key == 'P'+str(i+1):
          self._npipes += 1
          break

  def _setHp(self):
    """
    Set h of a pumb
    """
    if self._data['Pu']['h'] == "":
      if self._data['Pu']['P'] != '' and self._data['Q'] != '':
        self._data['Pu']['h'] = plib.head(self._data['Pu']['ef'], self._data['Q'], self._data['Pu']['P'], self._g, self._data['rho']) 
      else:
        self._data['Pu']['h'] = 0.
    #print(self._data['P'+str(i)]['Pu']['h'])

  def _setHt(self):
    """
    Set h of a turbine
    """
    for i in range(1,self._npipes+1):
      if self._data['P'+str(i)]['Tu']['h'] == "":
        if self._data['P'+str(i)]['Tu']['P'] != '' and self._data['Q'] != '':
          self._data['P'+str(i)]['Tu']['h'] = -1.*plib.head(self._data['P'+str(i)]['Tu']['ef'], self._data['Q'], self._data['P'+str(i)]['Tu']['P'], self._g, self._data['rho']) 
        else:
          self._data['P'+str(i)]['Tu']['h'] = 0.
      #print(self._data['P'+str(i)]['Tu']['h'])
  
  def _setE1(self):
    """
    Estimate the total energy at the entrance section
    """
    if self._data['E1']['p'] == "":
      self._E1 = ""
    else:
      self._E1 = self._data['E1']['z'] +  self._data['E1']['p'] + self._data['E1']['v']

  def _setE2(self):
    """
    Estimate the total energy at the end section
    """
    if self._data['E2']['p'] == "":
      self._E2 = ""
    else:
      self._E2 = self._data['E2']['z'] +  self._data['E2']['p'] + self._data['E2']['v']

  def _setSK(self):
    """
    Estimate the total of accesory K
    """
    self._SK = {}
    for i in range(1,self._npipes+1):
      self._SK['P'+str(i)] = sum(self._data['P'+str(i)]['K'])   
      #print(self._SK['P'+str(i)])

  def _setGravity(self):
    """
    Set the gravity constant
    """
    self._g = plib.gravity(self._data['US'])


class ParallelPipes():

  def __init__(self):

    # Set the input data
    self._data = InputData()._data
    self._npipes = InputData()._npipes
    self._E1 = InputData()._E1
    self._E2 = InputData()._E2
    self._SK = InputData()._SK
    self._g = InputData()._g
    self._rel = InputData()._rel

    # Executing de calculation
    self.procedure()

  def procedure(self):
    if self._data["PT"] ==1:
      print('')
      print('Proving the design of a parallel pipe system')
      print('')
      self.designTest()
    elif self._data["PT"] ==2:
      print('')
      print('Estimating the power in parallel pipes')
      print('')
      self.systemPower()
    elif self._data["PT"] ==3:
      print('')
      print('Design of a parallel pipe system')
      print('')
      self.pipeDesign()
      
  def designTest(self): 
    """
    Estimate de initial discharge in parallel pipes
    """
    
    Q = [0]*self._npipes
    he = [0]*self._npipes
    hf = [0]*self._npipes
    V  = [0]*self._npipes
    f  = [0]*self._npipes
    Re = [0]*self._npipes

    for i in range(1,self._npipes+1): 
      if self._data['IM'] == 'fp':
        res = plib.f_fp2(self._g, self._data['P'+str(i)]['ks'], self._data['rho'], self._data['mu'], self._data['P'+str(i)]['D'], self._E1, self._E2, self._data['Pu']['h'], self._data['P'+str(i)]['Tu']['h'], self._data['P'+str(i)]['L'], self._SK['P'+str(i)])
      elif self._data['IM'] == 'nr': 
        res = plib.f_nr2(self._g, self._data['P'+str(i)]['ks'], self._data['rho'], self._data['mu'], self._data['P'+str(i)]['D'], self._E1, self._E2, self._data['Pu']['h'], self._data['P'+str(i)]['Tu']['h'], self._data['P'+str(i)]['L'], self._SK['P'+str(i)])

      print(' ')
      print('Results of iteration for pipe %d' %i)
      print(' ')
      print(pd.DataFrame(list(zip(res['fl'],res['Vl'],res['hfrl'])), columns=['f', 'V', 'hf'], index=["{:d}".format(x) for x in range(1,len(res['fl'])+1)]))
   
      # Set variables 
      V[i-1] = res['V']
      f[i-1] = res['f']
      hf[i-1] = res['hfrl'][-1]

      # Estimate accesory losses
      he[i-1] = plib.he(self._g,self._SK['P'+str(i)],V[i-1])

      # Discharge estimation
      Q[i-1] =  plib.Qc(V[i-1], self._data['P'+str(i)]['D']) 

      # Estimate Re
      Re[i-1] = plib.Re(self._data['rho'], self._data['mu'], self._data['P'+str(i)]['D'], V[i-1])

    # Asign total discharge
    self._data['Q'] = sum(Q)

    # Printing results at iteration
    print(' ')
    print('Summary of results')
    print(' ')
    print(pd.DataFrame(list(zip(hf,V,Q,he,f,Re)), columns=['hf', 'V', 'Q','he','f','Re'], index=["P{:d}".format(x) for x in range(1,self._npipes+1)]))
    print('Qt = %8.4f m³/s' % self._data['Q'])

   
  def systemPower(self):
    """
    Estimate the system power in parallel pipes. Estimate the presure in the upstream or downstream node.
    """

    Q = [0]*self._npipes
    he = [0]*self._npipes
    hf = [0]*self._npipes
    V  = [0]*self._npipes
    f  = [0]*self._npipes
    Re = [0]*self._npipes

    # Set the initial discharge for P1
    SD_L = 0.
    for i in range(1,self._npipes+1): 
      SD_L += plib.D_L(self._data['P'+str(i)]['D'],self._data['P'+str(i)]['L'])
    Q[0] = self._data['Q']*plib.D_L(self._data['P1']['D'],self._data['P1']['L'])/SD_L

    j = 1
    while True:
      # Calculate de velocity
      V[0] = plib.Vc(Q[0], self._data['P1']['D'])
      
      # Estimate he
      he[0] = plib.he(self._g, self._SK['P1'], V[0])

      # Estimate f
      if self._data['IM'] == 'fp':
        self._fdic = plib.f_fp(self._g, self._data['P1']['ks'], self._data['rho'], self._data['mu'], self._data['P1']['D'], V[0])
      elif self._data['IM'] == 'nr': 
        self._fdic = plib.f_nr(self._g, self._data['P1']['ks'], self._data['rho'], self._data['mu'], self._data['P1']['D'], V[0])

      # Get f
      f[0] = self._fdic['f']

      # Estimate Re
      Re[0] = plib.Re(self._data['rho'], self._data['mu'], self._data['P1']['D'], V[0])

      # Estimate hf
      hf[0] = plib.hf(self._g, f[0], self._data['P1']['L'], self._data['P1']['D'], V[0])

      # Updating the E1
      if self._data['E1']['p'] == "":
        self._E1 = self._E2 + hf[0] + he[0] + self._data['P1']['Tu']['h']
      else:
        self._E2 = self._E1 - hf[0] - he[0] - self._data['P1']['Tu']['h']
      
      # Loop for the other pipes
      for i in range(2,self._npipes+1): 
        if self._data['IM'] == 'fp':
          res = plib.f_fp2(self._g, self._data['P'+str(i)]['ks'], self._data['rho'], self._data['mu'], self._data['P'+str(i)]['D'], self._E1, self._E2, self._data['Pu']['h'], self._data['P'+str(i)]['Tu']['h'], self._data['P'+str(i)]['L'], self._SK['P'+str(i)])
        elif self._data['IM'] == 'nr': 
          res = plib.f_nr2(self._g, self._data['P'+str(i)]['ks'], self._data['rho'], self._data['mu'], self._data['P'+str(i)]['D'], self._E1, self._E2, self._data['Pu']['h'], self._data['P'+str(i)]['Tu']['h'], self._data['P'+str(i)]['L'], self._SK['P'+str(i)])

        # Set variables 
        V[i-1] = res['V']
        f[i-1] = res['f']
        hf[i-1] = res['hfrl'][-1]

        # Estimate accesory losses
        he[i-1] = plib.he(self._g, self._SK['P'+str(i)], V[i-1])

        # Discharge estimation
        Q[i-1] =  plib.Qc(V[i-1], self._data['P'+str(i)]['D']) 

        # Estimate Re
        Re[i-1] = plib.Re(self._data['rho'], self._data['mu'], self._data['P'+str(i)]['D'], V[i-1])

      # Printing results
      print('Results of iteration %d' % j)
      print('')
      print(pd.DataFrame(list(zip(hf,V,Q,he,f,Re)), columns=['hf', 'V', 'Q','he','f','Re'], index=["P{:d}".format(x) for x in range(1,self._npipes+1)]))
      print('')

      # Addition of estimate discharges 
      Qn = sum(Q)
      
      if (abs(self._data['Q']-Qn)) < plib.ERROR:
        break

      # Update discharge for P1
      Q[0] = Q[0]*self._data['Q']/Qn

      j += 1

    # Nominal system power
    if self._data['E1']['p'] == "":
      print("Pressure head in node 1 = %8.2f (m)" % self._E1)
      print("Pressure in node 1 = %8.2f (Pa)" % (self._E1*self._g*self._data['rho']))
    else:
      print("Pressure head in node 2 = %8.2f (m)" % self._E2)
      print("Pressure in node 2 = %8.2f (Pa)" % (self._E2*self._g*self._data['rho']))
      


  def pipeDesign(self):
    """
    Estimation of the diameter of a new parallel pipe to the existing one.
    """

    CD={'4':101.6,'6':152.4,'8':203.2,'10':254,'12':304.8,'14':355.6,'16':406.4}   

    # Loop to find the optimal comertial diameter of ['P'+str(self._npipes)] (the new pipe)
    print('Design of pipe %d' % self._npipes )
    V = []
    f = []
    hf = []
    he = []
    Qnl = []
    Dinl = []
    j = 1
    for Din, self._data['P'+str(self._npipes)]['D'] in CD.items():
      self._data['P'+str(self._npipes)]['D'] *= 0.001 
      if self._data['IM'] == 'fp':
        self._res = plib.f_fp2(self._g, self._data['P'+str(self._npipes)]['ks'], self._data['rho'], self._data['mu'], self._data['P'+str(self._npipes)]['D'], self._E1, self._E2, self._data['Pu']['h'], self._data['P'+str(self._npipes)]['Tu']['h'], self._data['P'+str(self._npipes)]['L'], self._SK['P'+str(self._npipes)])
      elif self._data['IM'] == 'nr': 
        self._res = plib.f_nr2(self._g, self._data['P'+str(self._npipes)]['ks'], self._data['rho'], self._data['mu'], self._data['P'+str(self._npipes)]['D'], self._E1, self._E2, self._data['Pu']['h'], self._data['P'+str(self._npipes)]['Tu']['h'], self._data['P'+str(self._npipes)]['L'], self._SK['P'+str(self._npipes)])

      Dinl.append(Din)

      # Set variables 
      V.append(self._res['V'])
      f.append(self._res['f'])
      hf.append(self._res['hfrl'][-1])

      # Estimate accesory losses
      he.append(plib.he(self._g,self._SK['P'+str(self._npipes)],self._res['V']))

      # Discharge estimation
      Qn =  plib.Qc(self._res['V'], self._data['P'+str(self._npipes)]['D']) 
      Qnl.append(Qn)

      if Qn >= self._data['P'+str(self._npipes)]['Q']:
        break
      
      j += 1 
 
    print(' ')
    print(pd.DataFrame(list(zip(Dinl,hf,V,Qnl,he,f)), columns=['D"','hf', 'V', 'Q','he','f'], index=["Iter {:d}".format(x) for x in range(1,j+1)]))
    print('')


    # Set the initial discharge for P+str(self._npipes)
    Q = [0]*self._npipes
    SD_L = 0.
    for i in range(1,self._npipes+1): 
      SD_L += plib.D_L(self._data['P'+str(i)]['D'],self._data['P'+str(i)]['L'])
    Q[self._npipes-1] = self._data['Q']*plib.D_L(self._data['P'+str(self._npipes)]['D'],self._data['P'+str(self._npipes)]['L'])/SD_L


    he = [0]*self._npipes
    V  = [0]*self._npipes
    f  = [0]*self._npipes
    he = [0]*self._npipes

    j = 1
    while True:

      # Estimations for P+str(self._npipes), the new pipe
      # Calculate de velocity 
      V[self._npipes-1] = plib.Vc(Q[self._npipes-1], self._data['P'+str(self._npipes)]['D'])
      
      # Estimate he
      he[self._npipes-1] = plib.he(self._g, self._SK['P'+str(self._npipes)], V[self._npipes-1])

      # Estimate f
      if self._data['IM'] == 'fp':
        self._fdic = plib.f_fp(self._g, self._data['P'+str(self._npipes)]['ks'], self._data['rho'], self._data['mu'], self._data['P'+str(self._npipes)]['D'], V[self._npipes-1])
      elif self._data['IM'] == 'nr': 
        self._fdic = plib.f_nr(self._g, self._data['P'+str(self._npipes)]['ks'], self._data['rho'], self._data['mu'], self._data['P'+str(self._npipes)]['D'], V[self._npipes-1])

      # Get f
      f[self._npipes-1] = self._fdic['f']

      # Estimate hf
      hf[self._npipes-1] = plib.hf(self._g, f[self._npipes-1], self._data['P'+str(self._npipes)]['L'], self._data['P'+str(self._npipes)]['D'], V[self._npipes-1])

      # Updating energy at node 2
      self._E2 = self._E1-hf[self._npipes-1]-he[self._npipes-1]

      # Estimate of Q for i=1...self._npipes-1
      for i in range(1,self._npipes): 
        if self._data['IM'] == 'fp':
          res = plib.f_fp2(self._g, self._data['P'+str(i)]['ks'], self._data['rho'], self._data['mu'], self._data['P'+str(i)]['D'], self._E1, self._E2, self._data['Pu']['h'], self._data['P'+str(i)]['Tu']['h'], self._data['P'+str(i)]['L'], self._SK['P'+str(i)])
        elif self._data['IM'] == 'nr': 
          res = plib.f_nr2(self._g, self._data['P'+str(i)]['ks'], self._data['rho'], self._data['mu'], self._data['P'+str(i)]['D'], self._E1, self._E2, self._data['Pu']['h'], self._data['P'+str(i)]['Tu']['h'], self._data['P'+str(i)]['L'], self._SK['P'+str(i)])

        #print(' ')
        #print('Results of iteration for pipe %d' %i)
        #print(' ')
        #print(pd.DataFrame(list(zip(res['fl'],res['Vl'],res['hfrl'])), columns=['f', 'V', 'hf'], index=["{:d}".format(x) for x in range(1,len(res['fl'])+1)]))
   
        # Set variables 
        V[i-1] = res['V']
        f[i-1] = res['f']
        hf[i-1] = res['hfrl'][-1]

        ## Estimate accesory losses
        he[i-1] = plib.he(self._g,self._SK['P'+str(i)],V[i-1])

        ## Discharge estimation
        Q[i-1] =  plib.Qc(V[i-1], self._data['P'+str(i)]['D']) 


      # Printing results
      print('Results of iteration %d' % j)
      print('')
      print(pd.DataFrame(list(zip(hf,V,Q,he,f)), columns=['hf', 'V', 'Q','he','f'], index=["P{:d}".format(x) for x in range(1,self._npipes+1)]))
      print('')

      # Addition of estimate discharges 
      Qn = sum(Q)
      if (abs(self._data['Q']-Qn)) < plib.ERROR:
        break

      # Update discharge for P1
      Q[self._npipes-1] = Q[self._npipes-1]*self._data['Q']/Qn

      j += 1

    print('Energy head at node 2 = %8.4f (m)' % self._E2)
