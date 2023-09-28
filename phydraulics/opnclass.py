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
    
    # Count the number of reservoirs
    self._getNreservoirs()
  
    # Count the number of nodes
    self._getNnodes()

    # Count the number of pipes 
    self._getNpipes()

    # Set gravity
    self._setGravity()

    # Set kinematic viscosity
    if self._data['nu'] != '':
      self._data['mu'] = plib.mu(self._data['rho'],self._data['nu'])
      
    # Set pumb head
    self._setHp() 

    # Get reservoir or other nodes connected to each node
    self._getConnectToNode()

    # Get initial node altitude
    #self._getInitialZNode()
 
    # Get the initial in and out pipes in nodes
    self._getNodeInOutPipe()

    # Set summatory of accesory Ks
    self._setSK()

  def _getNreservoirs(self):
    """
    Get the number of reservoirs 
    """
    self._nreser = 0
    for i in range(len(self._data)):
      for key in self._data:
        if key == 'RE'+str(i+1):
          self._nreser += 1
          break


  def _getNnodes(self):
    """
    Get the number of nodes
    """
    self._nnodes = 0
    for i in range(len(self._data)):
      for key in self._data:
        if key == 'N'+str(i+1):
          self._nnodes += 1
          break


  def _getNpipes(self):
    """
    Get the number of pipes
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

  def _setSK(self):
    """
    Estimate the total of accesory K
    """
    self._SK = {}
    for i in range(1,self._npipes+1):
      self._SK['P'+str(i)] = sum(self._data['P'+str(i)]['K'])   

  def _getNodeInOutPipe(self):
    """
    Get the pipes that flow in and out of nodes
    """
    self._inoutN = {}

    #print(self._resCoN)
    for key, value in self._resCoN.items():
      pin = []
      pout = []
      pinout = {}
      for i in value:
        for j in range(1,self._npipes+1):
          if (self._data['P'+str(j)]['S'] == key and self._data['P'+str(j)]['E'] == i) or (self._data['P'+str(j)]['E'] == key and self._data['P'+str(j)]['S'] == i):
            break
        if 'N' in i:
          if self._data[i]['z'] >= self._data[key]['z'] + self._data['P'+str(j)]['Pu']['h']:
            pin.append('P'+str(j))
          else:
            pout.append('P'+str(j))
        else:
          if self._data[i]['z'] >= self._data[key]['z'] + self._data['P'+str(j)]['Pu']['h']:
            pin.append('P'+str(j))
          else:
            pout.append('P'+str(j))
      pinout['in'] = pin
      pinout['out'] = pout
      self._inoutN[key] = pinout  
          
#  def _getNodeInOutPipe(self):
#    """
#    Get the pipes that flow in and out of nodes
#    """
#    self._inoutN = {}
#    for j in range(1,self._nnodes+1):
#      pin = []
#      pout = []
#      pinout = {}
#      for i in range(1,self._npipes+1):
#        if self._data['P'+str(i)]['S'] == "N"+str(j):
#          pout.append('P'+str(i))
#        if self._data['P'+str(i)]['E'] == "N"+str(j):
#          pin.append('P'+str(i))
#      pinout['in'] = pin
#      pinout['out'] = pout
#      self._inoutN['N'+str(j)] = pinout  

  def _getConnectToNode(self):
    """
    Get the reservoir connected to nodes throught pipes
    """

    self._resCoN = {}
    for i in range(1,self._nnodes+1):
      resN = []
      for j in range(1,self._npipes+1):
        for k in range(1,self._nreser+1):
          if (self._data['P'+str(j)]['S'] == "N"+str(i) and self._data['P'+str(j)]['E'] == "RE"+str(k)) or (self._data['P'+str(j)]['S'] == "RE"+str(k) and self._data['P'+str(j)]['E'] == "N"+str(i)):
            resN.append('RE'+str(k))
            break
        for l in range(1,self._nnodes+1):
          if (self._data['P'+str(j)]['S'] == "N"+str(i) and self._data['P'+str(j)]['E'] == "N"+str(l)) or (self._data['P'+str(j)]['S'] == "N"+str(l) and self._data['P'+str(j)]['E'] == "N"+str(i)):
            resN.append('N'+str(l))
            break
      self._resCoN['N'+str(i)] = resN  
  
#  def _getReserConnectToNode(self):
#    """
#    Get the reservoir connected to nodes throught pipes
#    """
#
#    self._resCoN = {}
#    for i in range(1,self._nnodes+1):
#      resN = []
#      for j in range(1,self._npipes+1):
#        for k in range(1,self._nreser+1):
#          if (self._data['P'+str(j)]['S'] == "N"+str(i) and self._data['P'+str(j)]['E'] == "RE"+str(k)) or (self._data['P'+str(j)]['S'] == "RE"+str(k) and self._data['P'+str(j)]['E'] == "N"+str(i)):
#            resN.append('RE'+str(k))
#            break
#      self._resCoN['N'+str(i)] = resN  

#  def _getInitialZNode(self):
#    """
#    Get the initial altitude of nodes
#    """
#    for key, value in self._resCoN.items():
#      zs = []
#      for i in value:
#        if 'N' not in i:
#          zs.append(self._data[i]["z"])
#
#      hps = []
#      for j in range(1,self._npipes+1):
#        if key in self._data['P'+str(j)]['S']:
#          hps.append(self._data['P'+str(j)]['Pu']['h'])
#
#      if key == 'N1':
#        zss = sorted(zs, reverse=True)
#        zss = zss[:-1]
#        self._data[key]['z'] = sum(zss)/len(zss) - sum(hps)/len(hps)
#      else:
#        self._data[key]['z'] = max(zs) + 0.3*((sum(zss)/len(zss))-max(zs)) + sum(hps)/len(hps)
#
#    #sys.exit()

  def _setGravity(self):
    """
    Set the gravity constant
    """
    self._g = plib.gravity(self._data['US'])


class OpenPipeNet():

  def __init__(self):

    # Set the input data
    self._data   = InputData()._data
    self._nreser = InputData()._nreser
    self._nnodes = InputData()._nnodes
    self._npipes = InputData()._npipes
    self._inoutN = InputData()._inoutN
    self._SK     = InputData()._SK
    self._g      = InputData()._g
    self._resCoN = InputData()._resCoN

    # Executing de calculation
    self.procedure()

  def procedure(self):
    if self._data["PT"] ==1:
      print('')
      print('Proving the design of a open pipe network')
      print('')
      self.designTest()
    elif self._data["PT"] ==3:
      print('')
      print('Design of a open pipe network')
      print('')
      self.pipeDesign()

  def getStarEndPipes(self, node):
    """
    Get the start point and end point of pipes connected to node
    """
    for i in range(1,self._npipes+1):
      if (self._data['P'+str(i)]['S'] == node or self._data['P'+str(i)]['E'] == node):
          stat = self._data['P'+str(i)]['S']
          endd = self._data['P'+str(i)]['E']
          if self._data[stat]['z'] + self._data['P'+str(i)]['Pu']['h'] < self._data[endd]['z']:
            self._data['P'+str(i)]['S'] = endd
            self._data['P'+str(i)]['E'] = stat
            
  def designTest(self): 
    """
    Estimate the discharges in open pipe network
    """

    # Initializing the node head correction
    Dzi = {} 
    for i in range(1,self._nnodes+1):
      Dzi['N'+str(i)] = 100.

    # Loop throught up to convergencie
    itera = 1
    while True:
      Dzf = {}
      Qi = {}
      Qo = {}
      InOut = {}

      print('')
      print('ITERATION No.: %d' % itera)
      print('')
      # Loop through the nodes
      for i in range(1,self._nnodes+1):

        # Loop to get the H of pipes in and out
        for j in self._inoutN['N'+str(i)]:
          if j == 'in':
            Hin = {}
            for k in self._inoutN['N'+str(i)][j]:
              res = self._data[k]['S']
              Hin[k] = self._data[res]['z'] - self._data['N'+str(i)]['z']
          elif j == 'out':
            Hout = {}
            for k in self._inoutN['N'+str(i)][j]:
              res = self._data[k]['E']
              Hout[k] = self._data['N'+str(i)]['z'] - self._data[res]['z']
        
        # Loop to estimate the pipe in discharges
        Qin={}
        Vin={}
        fin={}
        for key, value in Hin.items():
          if value != 0:
            if self._data['IM'] == 'fp':
              self._res = plib.f_fp2(self._g, self._data[key]['ks'], self._data['rho'], self._data['mu'], self._data[key]['D'], value, 0., self._data[key]['Pu']['h'], 0., self._data[key]['L'], self._SK[key])
            elif self._data['IM'] == 'nr': 
              self._res = plib.f_nr2(self._g, self._data[key]['ks'], self._data['rho'], self._data['mu'], self._data[key]['D'], value, 0., self._data[key]['Pu']['h'], 0., self._data[key]['L'], self._SK[key])
            Qin[key] =  plib.Qc(self._res['V'], self._data[key]['D']) 
            Vin[key] =  self._res['V'] 
            fin[key] =  self._res['f'] 
          else:
            Qin[key] = 0.0
            Vin[key] = 0.0
            fin[key] = 0.0
        #Qi['N'+str(i)] = Qin 

        # Loop to estimate the pipe out discharges
        Qout={}
        Vout={}
        fout={}
        for key, value in Hout.items():
          if value != 0:
            if self._data['IM'] == 'fp':
              self._res = plib.f_fp2(self._g, self._data[key]['ks'], self._data['rho'], self._data['mu'], self._data[key]['D'], value, 0., self._data[key]['Pu']['h'], 0., self._data[key]['L'], self._SK[key])
            elif self._data['IM'] == 'nr': 
              self._res = plib.f_nr2(self._g, self._data[key]['ks'], self._data['rho'], self._data['mu'], self._data[key]['D'], value, 0., self._data[key]['Pu']['h'], 0., self._data[key]['L'], self._SK[key])
            Qout[key] = plib.Qc(self._res['V'], self._data[key]['D']) 
            Vout[key] =  self._res['V'] 
            fout[key] =  self._res['f'] 
          else:
            Qout[key] = 0.0
            Vout[key] = 0.0
            fout[key] = 0.0
        #Qo['N'+str(i)] = Qout

        print('---> Resulst for Node: %s' % 'N'+str(i))
        InOut = {'Q':{'In':Qin, 'Out':Qout},'H':{'In':Hin, 'Out':Hout},'V':{'In':Vin,'Out':Vout}, 'f':{'In':fin,'Out':fout}}
        print(pd.DataFrame.from_dict({(i,j): InOut[i][j] 
                           for i in InOut.keys() 
                           for j in InOut[i].keys()}))
        #sys.exit()

        # Estimation of DZ in node
        ## For pipes in
        Qins = 0
        Qire = 0
        for key, value in Qin.items():
          Qins += value 
          if Hin[key] != 0.:
            Qire += value/abs(Hin[key])
        ## For pipes out
        Qouts = 0
        Qore = 0
        for key, value in Qout.items():
          Qouts += value 
          if Hout[key] != 0.:
            Qore += value/abs(Hout[key])
        Dzf['N'+str(i)] = 2*(Qins-Qouts-self._data['N'+str(i)]['Q'])/(Qire+Qore)
        
        # Correct node head
        self._data['N'+str(i)]['z'] += Dzf['N'+str(i)]

        # Get the in and out pipes to nodes
        InputData._getNodeInOutPipe(self)

        # Set the start and end point of pipes
        self.getStarEndPipes('N'+str(i))

      # Check convergencie
      atru = 0 
      for i in range(1,self._nnodes+1):
        atru += abs(Dzf['N'+str(i)]-Dzi['N'+str(i)]) < plib.ERROR
      if atru == self._nnodes:
        break
      
      # Update Dzi
      for key, value in Dzf.items():
        Dzi[key] = value
      
      itera += 1 

  def pipeDesign(self):
    """
    Estimation of pipe diameter in open pipe network
    """

    #print(self._data)
    # Diametros comerciales
    CD={'2':50.8,'2.5':63.5,'3':76.2,'4':101.6,'6':152.4,'8':203.2,'10':254,'12':304.8,'14':355.6,'16':406.4,'18':457.2,'20':508.0,'24':609.6,'30':762.0,'36':914.4}   

    # Initializing the node head correction
    Dzi = {} 
    for i in range(1,self._nnodes+1):
      Dzi['N'+str(i)] = 100.

    # Loop throught up to convergencie
    #print(self._inoutN)
    itera = 1
    while True:
      Dzf = {}
      Qi = {}
      Qo = {}
      InOut = {}

      print('')
      print('ITERATION No.: %d' % itera)
      print('')
      # Loop through the nodes
      for i in range(1,self._nnodes+1):

        # Loop to get the H of pipes in and out
        for j in self._inoutN['N'+str(i)]:
          if j == 'in':
            Hin = {}
            for k in self._inoutN['N'+str(i)][j]:
              res = self._data[k]['S']
              Hin[k] = self._data[res]['z'] - self._data['N'+str(i)]['z']
          elif j == 'out':
            Hout = {}
            for k in self._inoutN['N'+str(i)][j]:
              res = self._data[k]['E']
              Hout[k] = self._data['N'+str(i)]['z'] - self._data[res]['z']
        
        #print(Hin)
        #print(Hout)
        # Loop to estimate the pipe in discharges
        Qin={}
        Vin={}
        fin={}
        Din={}
        for key, value in Hin.items():
          if value != 0:
            # Loop to find the optimal comertial diameter
            for Dpul, self._data[key]['D'] in CD.items():
              self._data[key]['D'] *= 0.001 # from mm to m
              if self._data['IM'] == 'fp':
                self._res = plib.f_fp2(self._g, self._data[key]['ks'], self._data['rho'], self._data['mu'], self._data[key]['D'], value, 0., self._data[key]['Pu']['h'], 0., self._data[key]['L'], self._SK[key])
              elif self._data['IM'] == 'nr': 
                self._res = plib.f_nr2(self._g, self._data[key]['ks'], self._data['rho'], self._data['mu'], self._data[key]['D'], value, 0., self._data[key]['Pu']['h'], 0., self._data[key]['L'], self._SK[key])

              # Test Q
              if plib.Qc(self._res['V'], self._data[key]['D']) >= self._data[key]['Q']:
                break

            #self._data[key]['Q'] = plib.Qc(self._res['V'], self._data[key]['D'])
            Qin[key] = plib.Qc(self._res['V'], self._data[key]['D'])
            Vin[key] = self._res['V'] 
            fin[key] = self._res['f'] 
            Din[key] = Dpul
          else:
            Qin[key] = 0.0
            Vin[key] = 0.0
            fin[key] = 0.0
            Din[key] = 0.0

        # Loop to estimate the pipe out discharges
        Qout={}
        Vout={}
        fout={}
        Dout={}
        for key, value in Hout.items():
          if value != 0:
            # Loop to find the optimal comertial diameter
            for Dpul, self._data[key]['D'] in CD.items():
              self._data[key]['D'] *= 0.001 # from mm to m
              if self._data['IM'] == 'fp':
                self._res = plib.f_fp2(self._g, self._data[key]['ks'], self._data['rho'], self._data['mu'], self._data[key]['D'], value, 0., self._data[key]['Pu']['h'], 0., self._data[key]['L'], self._SK[key])
              elif self._data['IM'] == 'nr': 
                self._res = plib.f_nr2(self._g, self._data[key]['ks'], self._data['rho'], self._data['mu'], self._data[key]['D'], value, 0., self._data[key]['Pu']['h'], 0., self._data[key]['L'], self._SK[key])
              # Test Q
              if plib.Qc(self._res['V'], self._data[key]['D']) >= self._data[key]['Q']:
                break

            #self._data[key]['Q'] = plib.Qc(self._res['V'], self._data[key]['D'])
            Qout[key] = plib.Qc(self._res['V'], self._data[key]['D'])
            Vout[key] = self._res['V'] 
            fout[key] = self._res['f'] 
            Dout[key] = Dpul
          else:
            Qout[key] = 0.0
            Vout[key] = 0.0
            fout[key] = 0.0
            Dout[key] = 0.0
        #Qo['N'+str(i)] = Qout

        print('---> Resulst for Node: %s' % 'N'+str(i))
        InOut = {'Q':{'In':Qin, 'Out':Qout},'H':{'In':Hin, 'Out':Hout},'V':{'In':Vin,'Out':Vout}, 'f':{'In':fin,'Out':fout}, 'D':{'In':Din,'Out':Dout}}
        print(pd.DataFrame.from_dict({(i,j): InOut[i][j] 
                           for i in InOut.keys() 
                           for j in InOut[i].keys()}))

        # Estimation of DZ in node
        ## For pipes in
        Qins = 0
        Qire = 0
        for key, value in Qin.items():
          Qins += value 
          if Hin[key] != 0.:
            Qire += value/abs(Hin[key])
        ## For pipes out
        Qouts = 0
        Qore = 0
        for key, value in Qout.items():
          Qouts += value 
          if Hout[key] != 0.:
            Qore += value/abs(Hout[key])
        Dzf['N'+str(i)] = 2*(Qins-Qouts-self._data['N'+str(i)]['Q'])/(Qire+Qore)
        
        # Correct node head
        #print(Dzf['N'+str(i)])
        self._data['N'+str(i)]['z'] += Dzf['N'+str(i)]
        #print(self._data['N'+str(i)]['z'])

        # Get the in and out pipes to nodes
        InputData._getNodeInOutPipe(self)

        #print(self._data)
        # Set the start and end point of pipes
        self.getStarEndPipes('N'+str(i))

      # Check convergencie
      atru = 0 
      for i in range(1,self._nnodes+1):
        atru += abs(Dzf['N'+str(i)]-Dzi['N'+str(i)]) < plib.ERROR
      if atru == self._nnodes:
        break
      
      # Update Dzi
      for key, value in Dzf.items():
        Dzi[key] = value
      
      itera += 1 

      #if itera == 3:
      #  sys.exit()


