#!/usr/bin/python3

import json
import pandas as pd
import sys
import math
import matplotlib.pyplot as plt
import numpy as np

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

    # Set discharte in pipes (only for PT=1 and PT=2)
    self._setPQ()

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
    self._L = 0
    for i in range(1,self._npipes+1): 
      self._L += self._data['P'+str(i)]['L']

    # Pipe relation
    self._rel = abs(self._data['E1']['z'] - self._data['E2']['z'])/self._L


  def _setPQ(self):
    """
    Set discharge in each pipe
    """
    self._Q = [0]*self._npipes
    if self._data['PT'] in [2,3]:
      for i in range(1,self._npipes+1): 
        self._Q[0] +=  self._data['P'+str(i)]['Qi'] + -1.*self._data['P'+str(i)]['Qo']         
      for i in range(2,self._npipes+1): 
        self._Q[i-1] =  self._Q[i-2] + self._data['P'+str(i)]['Qi'] + self._data['P'+str(i-1)]['Qo']

  def _getNpipes(self):
    """
    Count the number of serial pipes
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
    for i in range(1,self._npipes+1):
      if self._data['P'+str(i)]['Pu']['h'] == "":
        if self._data['P'+str(i)]['Pu']['P'] != '' and self._Q[i-1] != '':
          self._data['P'+str(i)]['Pu']['h'] = plib.head(self._data['P'+str(i)]['Pu']['ef'], self._Q[i-1], self._data['P'+str(i)]['Pu']['P'], self._g, self._data['rho']) 
        else:
          self._data['P'+str(i)]['Pu']['h'] = 0.
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
    self._SK = {}
    for i in range(1,self._npipes+1):
      self._SK['P'+str(i)] = sum(self._data['P'+str(i)]['K'])   
      #print(self._SK['P'+str(i)])

  def _setGravity(self):
    """
    Set the gravity constant
    """
    self._g = plib.gravity(self._data['US'])


class SerialPipes():

  def __init__(self):

    # Set the input data
    self._data = InputData()._data
    self._npipes = InputData()._npipes
    self._E1 = InputData()._E1
    self._E2 = InputData()._E2
    self._SK = InputData()._SK
    self._g = InputData()._g
    self._Q = InputData()._Q
    self._rel = InputData()._rel
    self._L = InputData()._L

    # Executing de calculation
    self.procedure()

  def procedure(self):
    if self._data["PT"] ==1:
      print('')
      print('Proving the design of a serial pipe system')
      print('')
      self.designTest()
    elif self._data["PT"] ==2:
      print('')
      print('Estimating the power in serial pipes')
      print('')
      self.systemPower()
    elif self._data["PT"] ==3:
      print('')
      print('Design of a serial pipe system')
      print('')
      self.pipeDesign()
      
  def designTest(self): 
    """
    Estimate de initial discharge in a serial pipe
    """

    he = [0]*self._npipes
    hf = [0]*self._npipes
    V  = [0]*self._npipes
    f  = [0]*self._npipes
    Re = [0]*self._npipes

    # Initialize hf1
    Ht = self._E1 - self._E2
    SL_D = 0
    for i in range(1,self._npipes+1):
      SL_D += plib.L_D(self._data['P'+str(i)]['L'], self._data['P'+str(i)]['D'])
    L_D1=plib.L_D(self._data['P1']['L'], self._data['P1']['D'])
    hf[0]=( Ht*L_D1/SL_D )
    j = 1
    while True:
      
      # Estimate the velocity in P1
      V[0] = plib.vel(self._g, self._data['P1']['ks'], self._data['rho'], self._data['mu'], self._data['P1']['D'], self._data['P1']['L'], hf[0])

      # Minors losses in P1
      he[0] = (plib.he(self._g, self._SK['P1'], V[0]))

      # Estimate the discharge in P1
      self._Q[0] = plib.Qc(V[0], self._data['P1']['D'])

      # Estimate f 
      f[0] = plib.f_dw(self._g, hf[0], self._data['P1']['L'], self._data['P1']['D'], V[0])

      # Estimate Re
      Re[0] = plib.Re(self._data['rho'], self._data['mu'], self._data['P1']['D'], V[0])

      for i in range(2,self._npipes+1): 
        # Estimate discharge
        self._Q[i-1] = self._Q[i-2] + self._data['P'+str(i-1)]['Qi'] + self._data['P'+str(i-1)]['Qo']         

        # Estimate velocity
        V[i-1] = plib.Vc(self._Q[i-1], self._data['P'+str(i)]['D'])
        
        # Estimate he
        he[i-1] = plib.he(self._g, self._SK['P'+str(i)], V[i-1])

        # Estimate f
        if self._data['IM'] == 'fp':
          self._fdic = plib.f_fp(self._g, self._data['P'+str(i)]['ks'], self._data['rho'], self._data['mu'], self._data['P'+str(i)]['D'], V[i-1])
        elif self._data['IM'] == 'nr': 
          self._fdic = plib.f_nr(self._g, self._data['P'+str(i)]['ks'], self._data['rho'], self._data['mu'], self._data['P'+str(i)]['D'], V[i-1])
        
        # Get f
        f[i-1] = self._fdic['f']

        # Estimate Re
        Re[i-1] = plib.Re(self._data['rho'], self._data['mu'], self._data['P'+str(i)]['D'], V[i-1])

        # Estimate hf
        hf[i-1]=(plib.hf(self._g, self._fdic['f'], self._data['P'+str(i)]['L'], self._data['P'+str(i)]['D'], V[i-1]))
        #print(self._g, self._fdic['f'], self._data['P'+str(i)]['L'], self._data['P'+str(i)]['D'], V)
      

      # Printing results at iteration
      print(' ')
      print('Iteration %d' % j)
      print(' ')
      print(pd.DataFrame(list(zip(hf,V,self._Q,he,f,Re)), columns=['hf', 'V', 'Q','he','f','Re'], index=["P{:d}".format(x) for x in range(1,self._npipes+1)]))

      H = sum(hf)+sum(he)
      if abs(Ht-H)<plib.ERROR:
        break

      hf[0]+=(Ht-H)*L_D1/SL_D 
      j+=1

    # Plotting energy line and hydraulic gradient line
    self.plotGHLandEL(hf,V,he)
   
  def systemPower(self):
    """
    Estimate the system power in a serial pipe
    """
    he = [0]*self._npipes
    hf = [0]*self._npipes
    V  = [0]*self._npipes
    f  = [0]*self._npipes
    Re = [0]*self._npipes
    Tu_h = [0]*self._npipes

    for i in range(1,self._npipes+1): 
      # Estimate discharge
      #if i == 1:
      #  Q[i-1] = self._data['Qt']
      #else:
      #  Q[i-1] = Q[i-2] + self._data['P'+str(i-1)]['Qi'] + self._data['P'+str(i-1)]['Qo']         

      # Calculate de velocity
      V[i-1] = plib.Vc(self._Q[i-1], self._data['P'+str(i)]['D'])
      
      # Estimate he
      he[i-1] = plib.he(self._g, self._SK['P'+str(i)], V[i-1])

      # Estimate f
      if self._data['IM'] == 'fp':
        self._fdic = plib.f_fp(self._g, self._data['P'+str(i)]['ks'], self._data['rho'], self._data['mu'], self._data['P'+str(i)]['D'], V[i-1])
      elif self._data['IM'] == 'nr': 
        self._fdic = plib.f_nr(self._g, self._data['P'+str(i)]['ks'], self._data['rho'], self._data['mu'], self._data['P'+str(i)]['D'], V[i-1])

      # Get f
      f[i-1] = self._fdic['f']

      # Estimate Re
      Re[i-1] = plib.Re(self._data['rho'], self._data['mu'], self._data['P'+str(i)]['D'], V[i-1])

      # Estimate hf
      hf[i-1]=(plib.hf(self._g, self._fdic['f'], self._data['P'+str(i)]['L'], self._data['P'+str(i)]['D'], V[i-1]))

      # Get energy extracted for turbines
      Tu_h[i-1] = self._data['P'+str(i)]['Tu']['h']

    # Printing results
    print(pd.DataFrame(list(zip(hf,V,self._Q,he,f,Re)), columns=['hf', 'V', 'Q','he','f','Re'], index=["P{:d}".format(x) for x in range(1,self._npipes+1)]))
    print('')

    # Total head energy deliver by a pumb from Bernoulli equation
    self._data['P1']['Pu']['h'] = plib.HPu(self._E1, self._E2, sum(he), sum(hf), sum(Tu_h))

    # Nominal system power
    self._data['P1']['Pu']['P'] = plib.pot(self._data['US'], self._data['P1']['Pu']['ef'], self._Q[0], self._data['P1']['Pu']['h'], self._g, self._data['rho'])
      
    print("hp = %8.2f (m)" % self._data['P1']['Pu']['h'])
    print("P = %8.2f (W)" % self._data['P1']['Pu']['P'])

    # Plotting energy line and hydraulic gradient line
    self.plotGHLandEL(hf,V,he)

  def pipeDesign(self):
    """
    Estimation of pipe diameter
    """

    if self._E1 == 0 and self._data['P1']['Pu']['h'] != 0:
      self._E1 = self._data['P1']['Pu']['h'] 
      self._data['P1']['Pu']['h'] = 0.

    # Estimating initial hfs
    hf = [0]*self._npipes
    cosT = math.cos(math.asin(self._rel))
    for i in range(1,self._npipes+1): 
      hf[i-1] = 1.*(self._E1-self._E2)*self._data['P'+str(i)]['L']*cosT/(self._L*cosT) # multiplied by 0.9 to reduce the initial losses. Is not in the original equation.

    # Comercial diameters
    #CD={'3/4':23.63,'1':30.20,'1 1/4':38.14,'1 1/2':43.68,'2':54.58,'2 1/12':66.07,'3':80.42,'4':103.42,'6':152.22,'8':198.21,'10':247.09,'12':293.07,'14':321.76,'16':367.70,'18':413.66,'20':459.64,'24':551.54}   
    CD={'4':101.6,'6':152.4,'8':203.2,'10':254,'12':304.8,'14':355.6,'16':406.4}   

    he = [0]*self._npipes
    V  = [0]*self._npipes
    f  = [0]*self._npipes
    Re = [0]*self._npipes

    hmvi=0.0
    j = 1
    while True:

      # Loop for each pipe
      Ein =  self._E1
      cdi = []
      for i in range(1,self._npipes+1): 

        # Set out enerty
        Eou = Ein - hf[i-1]

        # Loop to find the optimal comertial diameter
        for Din, self._data['P'+str(i)]['D'] in CD.items():

          self._data['P'+str(i)]['D'] *= 0.001 # from mm to m
          
          # Iteration method
          if self._data['IM'] == 'fp':
            self._res = plib.f_fp2(self._g, self._data['P'+str(i)]['ks'], self._data['rho'], self._data['mu'], self._data['P'+str(i)]['D'], Ein, Eou, self._data['P'+str(i)]['Pu']['h'], self._data['P'+str(i)]['Tu']['h'], self._data['P'+str(i)]['L'],self._SK['P'+str(i)])
          elif self._data['IM'] == 'nr': 
            self._res = plib.f_nr2(self._g, self._data['P'+str(i)]['ks'], self._data['rho'], self._data['mu'], self._data['P'+str(i)]['D'], Ein, Eou, self._data['P'+str(i)]['Pu']['h'], self._data['P'+str(i)]['Tu']['h'], self._data['P'+str(i)]['L'],self._SK['P'+str(i)])

          # Test Q
          if plib.Qc(self._res['V'], self._data['P'+str(i)]['D']) >= self._Q[i-1]:
            break
        
        cdi.append(Din)
        # Set energy at pipe entrance
        Ein = Eou

        # Real velocity 
        V[i-1] = plib.Vc(self._Q[i-1], self._data['P'+str(i)]['D']) 

        # Estimate f
        if self._data['IM'] == 'fp':
          self._fdic = plib.f_fp(self._g, self._data['P'+str(i)]['ks'], self._data['rho'], self._data['mu'], self._data['P'+str(i)]['D'], V[i-1])
        elif self._data['IM'] == 'nr': 
          self._fdic = plib.f_nr(self._g, self._data['P'+str(i)]['ks'], self._data['rho'], self._data['mu'], self._data['P'+str(i)]['D'], V[i-1])
        f[i-1] = self._fdic['f']

        # Estimate hf
        hf[i-1] = plib.hf(self._g, f[i-1], self._data['P'+str(i)]['L'], self._data['P'+str(i)]['D'], V[i-1])

        # Estimate accesory losses
        he[i-1] = plib.he(self._g,self._SK['P'+str(i)],V[i-1])

        # Estimate Re
        Re[i-1] = plib.Re(self._data['rho'], self._data['mu'], self._data['P'+str(i)]['D'], V[i-1])

      # Printing results
      print(' ')
      print('Iteration %d' % j)
      print(' ')
      print(pd.DataFrame(list(zip(cdi,hf,V,self._Q,he,f,Re)), columns=['D"','hf', 'V', 'Q','he','f','Re'], index=["P{:d}".format(x) for x in range(1,self._npipes+1)]))
      print('')

      # Checking the energy loss through the pipes
      hmvf = self._E1 - self._E2 - sum(hf) - sum(he)    
      print('Balance of energy at the end: %8.2f' % hmvf)
      if abs(hmvi-hmvf)<=plib.ERROR or hmvf<0.0 or j>10:
        break

      #if hmvf < 0.0: hmvf = 0.
      # Updatint hf
      hf = list(map(hmvf.__add__, hf))
      hmvi = hmvf

      j += 1 

    # Plotting energy line and hydraulic gradient line
    self.plotGHLandEL(hf,V,he)


  def plotGHLandEL(self,hf,V,he):
    """
    Plot the hydraulic gradient line and the energy line
    """

    xc = [0]
    xca = 0
    el = [self._E1]
    ela = el[0]
    hgl =[el[0]-(V[0]**2)/(2*self._g)] 
    hgla = hgl[0]
    for i in range(1,self._npipes+1):
      
      # Set the x coordinates
      xca += self._data['P'+str(i)]['L']
      xc.append(xca)
      xc.append(xca)

      # Set energy line
      ela-=hf[i-1]
      el.append(ela)
      ela-=he[i-1]
      el.append(ela)
        
      # Set hydraulic gradient line
      hgla-=hf[i-1]
      hgl.append(hgla)
      hgla-=he[i-1]
      hgl.append(hgla)
       
    # Plots
    plt.figure(figsize=(8,4))
    plt.plot(np.array(xc),np.array(el), color='red', label='Energy line', linewidth=0.5)
    plt.plot(np.array(xc),np.array(el),'.', color='red')
    plt.plot(np.array(xc),np.array(hgl), color='blue', label='Hydraulic gradient line', linewidth=0.5)
    plt.plot(np.array(xc),np.array(hgl), '.', color='blue')
    plt.grid(linestyle = '--', linewidth = 0.5)
    if self._data['US'] == 'IS':
      plt.xlabel("Pipe lenght (m)")
      plt.ylabel("Head (m)")
    else:
      plt.xlabel("Pipe lenght (ft)")
      plt.ylabel("Head (ft)")
    plt.legend()
    plt.show()
