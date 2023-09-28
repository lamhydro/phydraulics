#!/usr/bin/python3

import json
import pandas as pd
import sys
import math
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
    
    # Count the number of reservoirs
    self._getNreservoirs()
  
    # Count the number of nodes
    self._getNnodes()

    # Count the number of pipes 
    self._getNpipes()

    # Count the number of circuits 
    self._getNcircu()

    # Get pipes 
    self._getPipes()

    # Get nodes connected to nodes
    self._getConnectToNode()

    # Get pipes list in circuits 
    self._getPipesInCircu2()
    #print(self._pipesInC)

    # Get pipes and sign in each circuit
    self._getPipesInCircu()

    # Get the nodes with not fixed (unknown) node head
    self._getNoFixNode()

    # Get pipes connected to nodes
    self._getPipesConNode()

    # Set gravity
    self._setGravity()

    # Set kinematic viscosity
    if self._data['nu'] != '':
      self._data['mu'] = plib.mu(self._data['rho'],self._data['nu'])
      
    # Set pumb head
    self._setHp() 

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

  def _getNcircu(self):
    """
    Get the number of circuits
    """
    self._ncircu = 0
    for i in range(len(self._data)):
      for key in self._data:
        if key == 'C'+str(i+1):
          self._ncircu += 1
          break

  def _getPipesInCircu(self):
    """
    Get the pipes in the circuits
    """
    self._pipesC = {}
    self._signsC = {}
    for i in range(1,self._ncircu+1):
      nodes = self._data['C'+str(i)]
      nodes.append(nodes[0])
      pipes = []
      signs = []
      for j in range(len(nodes)-1):
        for k in range(1,self._npipes+1):
          ns = self._data['P'+str(k)]['S'] 
          ne = self._data['P'+str(k)]['E'] 
          if (ns == nodes[j] or ns == nodes[j+1]) and (ne == nodes[j] or ne == nodes[j+1]):
            pipes.append('P'+str(k)) 
            if ns == nodes[j+1] and ne == nodes[j]:
              signs.append(-1.0)
            elif ns == nodes[j] and ne == nodes[j+1]:
              signs.append(1.0)
            break
      self._pipesC['C'+str(i)] = pipes  
      self._signsC['C'+str(i)] = signs  

    #print(self._pipesC)
    #print(self._signsC)

  def _getPipesConNode(self):
    """
    Get the pipes connected to nodes
    """
    self._pipesCn = {}
    for i in range(1,self._nnodes+1):
      pipes = []
      for j in range(1,self._npipes+1):
        ns = self._data['P'+str(j)]['S'] 
        ne = self._data['P'+str(j)]['E'] 
        if ns == 'N'+str(i) or ne == 'N'+str(i):
          if 'P'+str(j) in self._pipesInC:
            pipes.append('P'+str(j))
      self._pipesCn['N'+str(i)] = pipes

  def _getPipes(self):
    """
    Get the pipes
    """
    self._pipes = []
    for i in range(len(self._data)):
      for key in self._data:
        if key == 'P'+str(i+1):
          self._pipes.append('P'+str(i+1))
          break

      
  def _getPipesInCircu2(self):
    """
    Get the pipes in a circuit
    """
    self._pipesInC = []
    for Pi in self._pipes:
      ns = self._data[Pi]['S']
      #ne = self._data[Pi]['E']
      pipes = self._pipes[:]
      pipes.pop(self._pipes.index(Pi))  
      for Pii in pipes:
        if self._data[Pii]['S'] == ns or self._data[Pii]['E'] == ns:
          #if Pi not in self._pipesInC:
          self._pipesInC.append(Pi)
          break

  def _getNoFixNode(self):
    """
    Get the nodes with not fixed node head
    """
    self._noHfixN = []
    znil = []
    for i in range(1,self._nnodes+1):
      if self._data['N'+str(i)]['t'] == "u":
        self._noHfixN.append('N'+str(i))

  def _getConnectToNode(self):
    """
    Get the nodes connected to nodes throught pipes
    """

    self._NCoN = {}
    for i in range(1,self._nnodes+1):
      NcN = []
      for j in range(1,self._npipes+1):
        for l in range(1,self._nnodes+1):
          if (self._data['P'+str(j)]['S'] == "N"+str(i) and self._data['P'+str(j)]['E'] == "N"+str(l)) or (self._data['P'+str(j)]['S'] == "N"+str(l) and self._data['P'+str(j)]['E'] == "N"+str(i)):
            NcN.append('N'+str(l))
            break
      self._NCoN['N'+str(i)] = NcN  
 
#  def _getNoFixNode(self):
#    """
#    Get the nodes with not fixed node head
#    """
#    self._noHfixN = []
#    znil = []
#    for i in range(1,self._nnodes+1):
#      self._noHfixN.append('N'+str(i))
#      if self._data['N'+str(i)]['z'] == "":
#        self._data['N'+str(i)]['z'] = 0.
#      znil.append(self._data['N'+str(i)]['z'])
#    imaxznil = znil.index(max(znil))
#    self._noHfixN.pop(imaxznil)
   
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
          

  def _setGravity(self):
    """
    Set the gravity constant
    """
    self._g = plib.gravity(self._data['US'])


class ClosePipeNet():

  def __init__(self):

    # Set the input data
    self._data   = InputData()._data
    self._nreser = InputData()._nreser
    self._nnodes = InputData()._nnodes
    self._npipes = InputData()._npipes
    self._ncircu = InputData()._ncircu
    self._SK     = InputData()._SK
    self._g      = InputData()._g
    self._pipesC = InputData()._pipesC
    self._signsC = InputData()._signsC
    self._pipesCn = InputData()._pipesCn
    self._noHfixN = InputData()._noHfixN
    self._NCoN = InputData()._NCoN


    print(self._pipesCn)
    print(self._NCoN)

    # Executing de calculation
    self.procedure()

  def procedure(self):
    if self._data["PT"] ==1:
      if self._data["ME"]=="HCQ":
        print('')
        print('Proving the design of a close pipe network: Hardy-Cross discharge correction method')
        print('')
        self.designTest_HCQ()
      elif self._data["ME"]=="HCH":
        print('')
        print('Proving the design of a close pipe network: Hardy-Cross head correction method')
        print('')
        self.designTest_HCH()
    elif self._data["PT"] ==3:
      print('')
      print('Design of a open pipe network')
      print('')
      self.pipeDesign()

  def initialQinPipes_HCQ(self):
    """
    """
    ln = []
    for i in range(1, self._nnodes+1): # Loop through nodes
      ni = 'N'+str(i)
      ln.append(ni)
      Q = 0.
      for j in range(1,self._npipes+1): # Loop through pipes
        pi = 'P'+str(j)
        ns = self._data[pi]['S']
        ne = self._data[pi]['E']
        if ni == ne:
          if self._data[pi]['Q'] != "": 
            Q += self._data[pi]['Q']
      Q -=self._data[ni]['Q']
      nls = self._NCoN[ni]
      sl = 0
      for kk in nls:
        if kk not in ln:
          sl += 1
      if sl == 0:
        break
      Qn = Q/sl
      #print(ni, Q)
      #sys.exit()
      for nii in self._NCoN[ni]: # Loop through nodes conected to node ni
        if nii not in ln:
          for j in range(1,self._npipes+1): # Loop through pipes
            pi = 'P'+str(j)
            ns = self._data[pi]['S']
            ne = self._data[pi]['E']
            if ni == ns and nii == ne:
              if self._data[pi]['Q'] == "":
                self._data[pi]['Q'] = Qn 
            elif ni == ne and nii == ns:
              if self._data[pi]['Q'] == "":
                self._data[pi]['Q'] = -1.*Qn 
      
#  def getStarEndPipes(self, node):
#    """
#    Get the start point and end point of pipes connected to node #    """ #    for i in range(1,self._npipes+1):
#      if (self._data['P'+str(i)]['S'] == node or self._data['P'+str(i)]['E'] == node):
#          stat = self._data['P'+str(i)]['S']
#          endd = self._data['P'+str(i)]['E']
#          if self._data[stat]['z'] + self._data['P'+str(i)]['Pu']['h'] < self._data[endd]['z']:
#            self._data['P'+str(i)]['S'] = endd
#            self._data['P'+str(i)]['E'] = stat
            
  def designTest_HCQ(self): 
    """
    Estimate the discharges in open pipe network using the Hardy-Cross discharge correction method
    """

    # Initializing the discharge in each pipe following mass conservation at nodes
    self.initialQinPipes_HCQ()
    for i in range(1, self._npipes+1):
      pi = 'P'+str(i)
      print(pi, self._data['P'+str(i)]['Q']) 
    #sys.exit()

    # Loop throught up to convergencie
    itera = 1
    while True:

      print('')
      print('ITERATION No.: %d' % itera)
      print('')

      # Loop through the circuits
      htt = 0
      htil = {}
      for i in range(1,self._ncircu+1):
        print('-> Circuit No.: %d' % i)
        
        # Loop through pipes in circuit
        hfl = []
        hel = []
        htl = []
        htql = []
        fl = []
        tub = []
        Ql = []
        for Pi,Si in zip(self._pipesC['C'+str(i)],self._signsC['C'+str(i)]):
          
          # Estimate the energy losses
          ## Estimate velocity
          V = self._data[Pi]['Q']*Si/plib.Ac(self._data[Pi]['D'])
          ## Estimate f
          if self._data['IM'] == 'fp':
            faux = plib.f_fp(self._g, self._data[Pi]['ks'], self._data['rho'], self._data['mu'], self._data[Pi]['D'], abs(V))
          elif self._data['IM'] == 'nr': 
            faux = plib.f_nr(self._g, self._data[Pi]['ks'], self._data['rho'], self._data['mu'], self._data[Pi]['D'], abs(V))
          f = faux['f']
          ## Estimate hf
          hf = plib.hf(self._g, f, self._data[Pi]['L'], self._data[Pi]['D'], V)
          if V<0.:
            hf*=-1.
          # Estimate he
          he = plib.he(self._g, self._SK[Pi], V)
          if V<0.:
            he*=-1.
          # Total losses
          hti = hf + he - self._data[Pi]['Pu']['h']

  
          fl.append(f)
          Ql.append(self._data[Pi]['Q']*Si)
          hfl.append(hf)
          hel.append(he)
          htl.append(hti)
          htql.append(hti/(self._data[Pi]['Q']*Si))
          tub.append(Pi)
          htil[Pi] = hti
        
          htt += hti
          #print(Pi, self._data[Pi]['Q']*Si,f,hf+he,(hf+he)/(self._data[Pi]['Q']*Si))

        print(pd.DataFrame(list(zip(Ql,fl,hfl,hel,htl,htql)), columns=['Q', 'f', 'hf','he','hf+he','(hf+he)/Q'], index=tub))
        # Discharge correction factor
        DQ = -sum(htl)/(2*sum(htql))
        if self._data['US'] == 'IS':
          print('Delta Q = %8.6f m³/s' % DQ)
        elif self._data['US'] == 'ES':
          print('Delta Q = %8.6f ft³/s' % DQ)
        print('')
        # Correcting discharge in circuit pipes
        for Pi,Si in zip(self._pipesC['C'+str(i)],self._signsC['C'+str(i)]):
          #sbe = np.sign(self._data[Pi]['Q'])
          self._data[Pi]['Q'] = self._data[Pi]['Q'] + DQ*Si
          #saf = np.sign(self._data[Pi]['Q'])
          #if sbe != saf:
          #  self._data[Pi]['Q']*=-1.

      if abs(htt)<=plib.ERROR:
      #if itera>1:
        break
      itera += 1
    
    print('Summmary of discharges')
    for i in range(1,self._npipes+1):
      if self._data['US'] == 'IS':
        print('Discharge in Pipe No. %d (P%d) = %8.5f l/s' % (i,i,self._data['P'+str(i)]['Q']*1000.))
      elif self._data['US'] == 'ES':
        print('Discharge in Pipe No. %d (P%d) = %8.5f ft³/s' % (i,i,self._data['P'+str(i)]['Q']))

    # Get one of the known node head
    for i in range(1,self._nnodes+1):
      nif = 'N'+str(i)
      if self._data[nif]['t'] == 'k':
        zif = self._data[nif]['z']
        break
 
    for key, val in self._NCoN.items():
      for i in val:
        for j in range(1,self._npipes+1):
          ns = self._data['P'+str(j)]['S']
          ne = self._data['P'+str(j)]['E']
          if (ns == key and ne == i) or (ns == i and ne == key):
            if self._data[i]['t'] == 'u':
              signi = 1.
              if htil['P'+str(j)]>0:
                signi = -1.
              self._data[i]['z'] = self._data[key]['z'] - np.sign(self._data['P'+str(j)]['Q'])*abs(htil['P'+str(j)])
              if self._data[i]['z']>zif:
                self._data[i]['z'] = self._data[key]['z'] + np.sign(self._data['P'+str(j)]['Q'])*abs(htil['P'+str(j)]) 
              self._data[i]['t'] = 'k'
              break
    
    print('')
    print('Summmary of node heads')
    for i in range(1,self._nnodes+1):
      if self._data['US'] == 'IS':
        print('Head in Node No. %d (N%d) = %8.5f (m)' % (i,i,self._data['N'+str(i)]['z']))
      elif self._data['US'] == 'ES':
        print('Head in Node No. %d (N%d) = %8.5f (ft)' % (i,i,self._data['N'+str(i)]['z']))

    
  def designTest_HCH(self): 
    """
    Estimate the discharges in open pipe network using the Hardy-Cross head correction method
    """

    # Loop throught up to convergencie
    itera = 1
    while True:

      print('')
      print('ITERATION No.: %d' % itera)
      print('')
      
      DZZ = 0
      #for i in range(2,self._nnodes+1):
      for ni in self._noHfixN:
        
        print('-> Node No.: %s' % ni)
        #ni = 'N'+str(i)
        zni = self._data[ni]['z']
        pipes = self._pipesCn[ni]
        Ql = []
        fl = []
        hfl = []
        hel = [] 
        Hil = []
        Hjl = []
        tub = []
        DQZ = 0.
        for Pi in pipes:
          ns = self._data[Pi]['S']
          ne = self._data[Pi]['E']
          zns = self._data[ns]['z']
          zne = self._data[ne]['z']
          if zns > zne:
            Ein = zns
            Eou = zne
          else:
            Ein = zne
            Eou = zns
          
          # Velocity estimation
          if self._data['IM'] == 'fp':
            res = plib.f_fp2(self._g, self._data[Pi]['ks'], self._data['rho'], self._data['mu'], self._data[Pi]['D'], Ein, Eou, self._data[Pi]['Pu']['h'], 0, self._data[Pi]['L'],self._SK[Pi])
          elif self._data['IM'] == 'nr': 
            res = plib.f_nr2(self._g, self._data[Pi]['ks'], self._data['rho'], self._data['mu'], self._data[Pi]['D'], Ein, Eou, self._data[Pi]['Pu']['h'], 0, self._data[Pi]['L'],self._SK[Pi])

          # Get direction flow
          if ni == ns:
            if zns > zne:
              signQ = -1
            else:
              signQ = 1
            Zj=zne
          elif ni == ne:
            if zne > zns:
              signQ = -1
            else:
              signQ = 1
            Zj=zns
          
          # Discharge estimation * signQ
          self._data[Pi]['Q'] = signQ*plib.Qc(res['V'], self._data[Pi]['D'])        

          DQZ += self._data[Pi]['Q']/(Zj-zni) 
          
          fl.append(res['f'])
          Ql.append(self._data[Pi]['Q'])
          hfl.append(res['hfrl'][-1])
          hel.append(plib.he(self._g, self._SK[Pi], res['V']))
          Hil.append(zni)
          Hjl.append(Zj)
          tub.append(Pi) 

        # Printing
        print(pd.DataFrame(list(zip(Ql,fl,hfl,hel,Hil,Hjl)), columns=['Q', 'f', 'hf','he','Hi','Hj'], index=tub))
    
        # Check mass balance at node
        DQ = sum(Ql)-self._data[ni]['Q']
        if self._data['US'] == 'IS':
          print('Delta Q = %8.6f m³/s' % DQ)
        elif self._data['US'] == 'ES':
          print('Delta Q = %8.6f ft³/s' % DQ)

        # Estimate node correction factor
        DZ = 2*DQ/DQZ 
        if self._data['US'] == 'IS':
          print('Delta H = %8.6f m' % DZ)
        elif self._data['US'] == 'ES':
          print('Delta H = %8.6f ft' % DZ)
        print('')

        # Correct node head
        self._data[ni]['z']+=DZ

        # Cumulative node head corrections
        DZZ +=abs(DZ)

      if DZZ <= plib.ERROR:
        break

      itera += 1

    # Summary of discharges
    print('Summmary of discharges')
    for i in range(1,self._npipes+1):
      if self._data['US'] == 'IS':
        print('Discharge in Pipe No. %d (P%d) = %8.5f (l/s)' % (i,i,self._data['P'+str(i)]['Q']*1000.))
      elif self._data['US'] == 'ES':
        print('Discharge in Pipe No. %d (P%d) = %8.5f (ft³/s)' % (i,i,self._data['P'+str(i)]['Q']))
    print('')
    print('Summmary of node heads')
    for i in range(1,self._nnodes+1):
      if self._data['US'] == 'IS':
        print('Head in Node No. %d (N%d) = %8.5f (m)' % (i,i,self._data['N'+str(i)]['z']))
      elif self._data['US'] == 'ES':
        print('Head in Node No. %d (N%d) = %8.5f (ft)' % (i,i,self._data['N'+str(i)]['z']))


