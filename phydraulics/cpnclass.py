#!/usr/bin/python3

import json
import pandas as pd
import sys
import math
import numpy as np
#import random

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
    Get the pipes in circuit connected to nodes
    """
    self._pipesCn = {}
    self._pipesCn2 = {}
    for i in range(1,self._nnodes+1):
      pipes = []
      pipes2 = []
      for j in range(1,self._npipes+1):
        ns = self._data['P'+str(j)]['S'] 
        ne = self._data['P'+str(j)]['E'] 
        if ns == 'N'+str(i) or ne == 'N'+str(i):
          pipes2.append('P'+str(j))
          if 'P'+str(j) in self._pipesInC:
            pipes.append('P'+str(j))
      self._pipesCn['N'+str(i)] = pipes
      self._pipesCn2['N'+str(i)] = pipes2


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
    self._pipesCn2 = InputData()._pipesCn2
    self._noHfixN = InputData()._noHfixN
    self._NCoN = InputData()._NCoN

    print(self._signsC)
    print(self._pipesC)
    print(self._pipesCn)
    print(self._pipesCn2)
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
      elif self._data["ME"]=="LP":
        print('')
        print('Proving the design of a close pipe network: Lineal Programming method')
        print('')
        self.designTest_LP()
    elif self._data["PT"] ==3:
      print('')
      print('Design of a open pipe network')
      print('')
      self.pipeDesign()

  def sumQinNodes(self):
    """
    """
    Qnt = 0
    for ni, pis in self._pipesCn2.items():
      Qni = 0
      for pi in pis:
        ns = self._data[pi]['S']
        ne = self._data[pi]['E']
        Q = self._data[pi]['Q']
        if Q>0.:
          if ne == ni:
            Qni += Q
          else:
            Qni -= Q
        else:
          if ns == ni:
            Qni += abs(Q)
          else:
            Qni -= abs(Q)
      Qni -= self._data[ni]['Q'] 
      Qnt += abs(Qni)
      #print(ni,Qni)
    #print('Qnt',Qnt)

    return Qnt

  def initialQinPipes_HCQ(self):
    """
    Initialize pipe discharges for Hardy-Cross method with Q corrections
    """
    for r in [rr/20 for rr in range(1,20)]:
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
          elif ni == ns:
            if self._data[pi]['Q'] != "": 
              if self._data[pi]['Q'] < 0.0:
                Q += abs(self._data[pi]['Q'])
              else:
                Q -= self._data[pi]['Q']

        Q -=self._data[ni]['Q']
        nls = self._NCoN[ni]
        sl = 0
        for kk in nls:
          if kk not in ln:
            sl += 1
        if sl == 0:
          break
        #Qn = []
        #for ii in range(sl):
        #  if ii == 0:
        #    Qn.append(r*Q) 
        #    if sl>1:
        #      Qii = (Q-(r*Q))/(sl-1)
        #  else:
        #    Qn.append(Qii)
        if ni == 'N1':
          Qn = []
          for ii in range(sl):
            if ii == 0:
              Qn.append(Q*r)
            else:
              Qn.append(Q*(1.-r)/(sl-1))
        else:
          Qn = Q/sl
        #Qn = Q/sl
        #print('here',ni,Qn)
        #print(ni, Q)
        #sys.exit()
        ii =0
        for nii in nls: # Loop through nodes conected to node ni
          if nii not in ln:
            for j in range(1,self._npipes+1): # Loop through pipes
              pi = 'P'+str(j)
              ns = self._data[pi]['S']
              ne = self._data[pi]['E']
              if ni == ns and nii == ne:
                if self._data[pi]['Q'] == "":
                  if ni == 'N1':
                    self._data[pi]['Q'] = Qn[ii]#Qn 
                  else:
                    self._data[pi]['Q'] = Qn 
              elif ni == ne and nii == ns:
                if self._data[pi]['Q'] == "":
                  if ni == 'N1':
                    self._data[pi]['Q'] = -1.*Qn[ii]#Qn 
                  else:
                    self._data[pi]['Q'] = -1.*Qn#Qn 
            ii+=1

        #for ki in self._pipesCn2[ni]:
        #  print('***',ki, self._data[ki]['Q'])
        #sys.exit()

      Qnt=self.sumQinNodes()
      #print('-------->',Qnt)
      if Qnt<1.0e-12:
        break
      for i in range(1, self._npipes+1):
        if i>1:
          self._data['P'+str(i)]['Q']= ""
 
        #print(r,Qnt)
 
#  def initialQinPipes_HCQ_2(self):
#    """
#    Initialize pipe discharges for Hardy-Cross method with Q corrections
#    """
#    #for r in [rr/20 for rr in range(1,20)]:
#    ln = []
#    for i in range(1, self._nnodes+1): # Loop through nodes
#      ni = 'N'+str(i)
#      ln.append(ni)
#      Q = 0.
#      for j in range(1,self._npipes+1): # Loop through pipes
#        pi = 'P'+str(j)
#        ns = self._data[pi]['S']
#        ne = self._data[pi]['E']
#        if ni == ne:
#          if self._data[pi]['Q'] != "": 
#            Q += self._data[pi]['Q']
#      Q -=self._data[ni]['Q']
#      nls = self._NCoN[ni]
#      sl = 0
#      for kk in nls:
#        if kk not in ln:
#          sl += 1
#      if sl == 0:
#        break
#      #Qn = []
#      #for ii in range(sl):
#      #  if ii == 0:
#      #    Qn.append(r*Q) 
#      #    if sl>1:
#      #      Qii = (Q-(r*Q))/(sl-1)
#      #  else:
#      #    Qn.append(Qii)
#      Qn = Q/sl
#      #print(Qn)
#      #print(ni, Q)
#      #sys.exit()
#      ii =0
#      for nii in self._NCoN[ni]: # Loop through nodes conected to node ni
#        if nii not in ln:
#          for j in range(1,self._npipes+1): # Loop through pipes
#            pi = 'P'+str(j)
#            ns = self._data[pi]['S']
#            ne = self._data[pi]['E']
#            if ni == ns and nii == ne:
#              if self._data[pi]['Q'] == "":
#                self._data[pi]['Q'] = Qn#[ii]#Qn 
#            elif ni == ne and nii == ns:
#              if self._data[pi]['Q'] == "":
#                self._data[pi]['Q'] = -1.*Qn#[ii]#Qn 
#          ii+=1
#      
#    Qnt=self.sumQinNodes()
#    print(Qnt)
#      #if Qnt<1.0e-8:
#      #  break
#      #for i in range(1, self._npipes+1):
#      #  if i>1:
#      #    self._data['P'+str(i)]['Q']= ""
# 
#      #print(r,Qnt)

  def initialNodeHead_HCH(self):
    """
    Set the initial node heads
    """
    Hn1 = self._data['N1']['z']
    ln = []
    for i in range(1,self._nnodes+1):
      ni = 'N'+str(i)
      z = self._data[ni]['z']
      ln.append(ni)
      nls = self._NCoN[ni]
      for nii in nls: # Loop through nodes conected to node ni
        if nii not in ln:
          self._data[nii]['z']=z*0.9
      #if i>1:
      #  self._data['N'+str(i)]['z'] = Hn1*random.randint(80,90)/100.
       
            
  def designTest_HCQ(self): 
    """
    Estimate the discharges in open pipe network using the Hardy-Cross discharge correction method
    """

    # Initializing the discharge in each pipe following mass conservation at nodes
    if self._data['P'+str(self._npipes)]['Q'] == '': 
      print('')
      print('Initial pipe discharges in the network')
      print('')
      self.initialQinPipes_HCQ()
      for i in range(1, self._npipes+1):
        pi = 'P'+str(i)
        print(pi, round(self._data['P'+str(i)]['Q'],3))

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
    # Initializing the node heads
    if self._data['N'+str(self._nnodes)]['z'] == '': 
      print('')
      print('Initial node heads in the network')
      print('')
      self.initialNodeHead_HCH() 
      for i in range(1, self._nnodes+1):
        ni = 'N'+str(i)
        print(ni, round(self._data['N'+str(i)]['z'],3))

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

  def designTest_LP(self): 
    """
    Estimate the discharges in open pipe network using the lineal programming method
    """

    # Initializing the discharge in each pipe following mass conservation at nodes
    if self._data['P'+str(self._npipes)]['Q'] == '': 
      print('')
      print('Initial pipe discharges in the network')
      print('')
      self.initialQinPipes_HCQ()
      for i in range(1, self._npipes+1):
        pi = 'P'+str(i)
        print(pi, round(self._data['P'+str(i)]['Q'],3))

    #self._data['P2']['Q'] = 0.1 
    #self._data['P3']['Q'] = 0.1 
    #self._data['P4']['Q'] = -0.1 
    #self._data['P5']['Q'] = -0.1 
    #self._data['P6']['Q'] = 0.1 
    #self._data['P7']['Q'] = 0.1 
    #self._data['P8']['Q'] = -0.1 

    # Set the matrix of zeros
    k = 0 
    pl = []
    for key, values in self._pipesC.items():
      for j in values:
        if j not in pl:
          pl.append(j)
          k+=1 
    
    #M = np.empty((k,k,))
    #M[:] = np.nan
    M = np.zeros((k,k,))
    #C = np.empty((k,))
    #C[:] = np.nan
    C = np.zeros((k,))
    #print(M)
    #print(C)
    #print(k)
    #print(pl)
    #sys.exit()
    
    # Loop throught up to convergencie
    itera = 1
    while True:

      print('')
      print('ITERATION No.: %d' % itera)
      print('')

      # Continuity equations at the nodes
      row =0
      for ni,pis in self._pipesCn2.items(): # Loop through pipes connected to nodes
        if row<self._nnodes-1:
          C[row]=self._data[ni]['Q']
        for pi in pis:
          ns = self._data[pi]['S']
          ne = self._data[pi]['E']
          if 'RE' in ns:
            C[row]=-self._data[pi]['Q']
          else:
            if ni == ns:
              if self._data[pi]['Q']>0:
                k = -1.
              else:
                k = 1.
            elif ni == ne:
              if self._data[pi]['Q']>0:
                k = 1.
              else:
                k = -1.
            ii = int(pi.replace('P',''))
            if row<self._nnodes-1:
              M[row][ii-2] = k
        row+=1 

      #print(M)
      #print(C)
      #print(row)

      # Energy conservation in the circuits
      #kijsA_= {}
      for i in range(1,self._ncircu+1):
        print('-> Circuit No.: %d' % i)
        
        # Loop through pipes in circuit
        #kijs_={}
        for Pi,Si in zip(self._pipesC['C'+str(i)],self._signsC['C'+str(i)]):
          
          # Estimate the energy losses
          ## Estimate velocity
          #V = self._data[Pi]['Q']*Si/plib.Ac(self._data[Pi]['D'])
          V = self._data[Pi]['Q']*Si/plib.Ac(self._data[Pi]['D'])
          ## Estimate f
          if self._data['IM'] == 'fp':
            faux = plib.f_fp(self._g, self._data[Pi]['ks'], self._data['rho'], self._data['mu'], self._data[Pi]['D'], abs(V))
          elif self._data['IM'] == 'nr': 
            faux = plib.f_nr(self._g, self._data[Pi]['ks'], self._data['rho'], self._data['mu'], self._data[Pi]['D'], abs(V))
          f = faux['f']
          ## 
          hfij = f*self._data[Pi]['L']/self._data[Pi]['D']
          kij_ = self._data[Pi]['Q']*Si*(hfij+self._SK[Pi])/(2*self._g*(plib.Ac(self._data[Pi]['D'])**2.))
          ii = int(Pi.replace('P',''))
          M[row-1][ii-2] = kij_
          #kijs_[Pi] = kij_
          #hf = plib.hf(self._g, f, self._data[Pi]['L'], self._data[Pi]['D'], V)
          #if V<0.:
          #  kij*=-1.
          ## Estimate he
          #he = plib.he(self._g, self._SK[Pi], V)
          #if V<0.:
          #  he*=-1.
        row+=1 
        #kijsA_['N'+str(i)]=kijs_ 
      #print(kijsA_)
      #print(M)
      #print(C)

      # Matrix inversion
      x = np.linalg.solve(M, C)
      Qoij = {}
      i = 0
      for i,pi in enumerate(pl):
        Qoij[pi] = x[i]
        i+=1
      print(Qoij)

      accu=0
      for pi in pl:
        #accu += abs(abs(self._data[pi]['Q'])-Qoij[pi])
        accu += abs(self._data[pi]['Q']-Qoij[pi])
      print('-->',accu)
      if accu <= plib.ERROR:
        break

      # Correcting pipe discharges
      for pi in pl:
        if self._data[pi]['Q']<0:
          sig = -1. 
        else:
          sig = 1.
        #self._data[pi]['Q'] = sig*0.5*(abs(self._data[pi]['Q']) + Qoij[pi])
        self._data[pi]['Q'] = Qoij[pi]
        #self._data[pi]['Q'] = 0.5*(abs(self._data[pi]['Q']) + Qoij[pi])
        #print(pi,self._data[pi]['Q'])
      #sys.exit()
      
      itera +=1
      #if itera>40:
      #  break
      #sys.exit()
    # Summary of discharges
    print('Summmary of discharges')
    for i in range(1,self._npipes+1):
      if self._data['US'] == 'IS':
        print('Discharge in Pipe No. %d (P%d) = %8.5f (l/s)' % (i,i,self._data['P'+str(i)]['Q']*1000.))
      elif self._data['US'] == 'ES':
        print('Discharge in Pipe No. %d (P%d) = %8.5f (ft³/s)' % (i,i,self._data['P'+str(i)]['Q']))
 
