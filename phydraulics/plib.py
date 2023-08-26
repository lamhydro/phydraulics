#!/usr/bin/python3

import math

# Global variables
ERROR=1.e-6 # error for iteration convergency
Fi=0.001     # seed value of friction factor f

def ks_d(ks,d):
  """
  Ratio ks/d
  """
  try:
    return ks/d
  except ValueError:
    print("Oops!  That was no valid number.  Try again...")

def nu(rho,mu):
  """
  Kinematic viscosity = mu/rho
  """
  try:
    return mu/rho
  except ValueError:
    print("Oops!  That was no valid number.  Try again...")

def mu(rho,nu):
  """
  Dinamic viscosity = nu*rho
  """
  try:
    return nu*rho
  except ValueError:
    print("Oops!  That was no valid number.  Try again...")

def Ac(D):
  """
  Wet area of circular pipe
  """
  try:
    return math.pi*(D**2)/4
  except ValueError:
    print("Oops!  That was no valid number.  Try again...")

def Pc(D):
  """
  Wet perimeter of circular pipe
  """
  try:
    return math.pi*D
  except ValueError:
    print("Oops!  That was no valid number.  Try again...")

def Rh(D):
  """
  Hydraulic ratio; area over perimeter
  """
  try:
    return Ac(D)/Pc(D)
  except ValueError:
    print("Oops!  That was no valid number.  Try again...")

def Re(rho, mu, D, V):
  """
  Reynolds number
  """
  try:
    return 4.*Rh(D)*V*rho/mu
  except ValueError:
    print("Oops!  That was no valid number.  Try again...")

def flowRegime(rho, mu, D, V):
  """
  Clasification of flow regime based on Reynolds number
  """
  try:
    Rey = Re(rho, mu, D, V)
    if Rey<=2000:
      return 'Laminar'
    elif Rey>2000 and Rey<=4000:
      return 'Transition'
    else:
      return 'Turbulent'
  except ValueError:
    print("Oops!  That was no valid number.  Try again...")

def hf(g,f,L,D,V):
  """
  Darcy-Weisbach equation
  """
  try:
    return f*(L/D)*(V**2)/(2*g)
  except ValueError:
    print("Oops!  That was no valid number.  Try again...")

def L_D(L,D):
  """
  Relation L/D^5. It is known that hf ~ L/D^5
  """
  try:
    return L/(D**5.)
  except ValueError:
    print("Oops!  That was no valid number.  Try again...")

def D_L(D,L):
  """
  Relation D^(5/2)/\sqrt(L). It is known that Q ~ D^(5/2)/\sqrt(L)
  """
  try:
    return (D**(5./2))/math.sqrt(L)
  except ValueError:
    print("Oops!  That was no valid number.  Try again...")


def he(g,K,V):
  """
  Minor loses
  """
  try:
    return K*(V**2)/(2.*g)
  except ValueError:
    print("Oops!  That was no valid number.  Try again...")

def Vc(Q,D):
  """
  Velocity as Q/A in a circular pipe
  """
  try:
    return Q/Ac(D)
  except ValueError:
    print("Oops!  That was no valid number.  Try again...")

def Qc(V,D):
  """
  Velocity as V*A in a circular pipe
  """
  try:
    return V*Ac(D)
  except ValueError:
    print("Oops!  That was no valid number.  Try again...")

def vel(g, ks, rho, mu, D, L, hf):
  """
  Velocity from the Colebrook-White
  """
  try:
    d1=-2*math.sqrt(2*g*D*hf)/(math.sqrt(L))
    d2=ks/(3.7*D)
    d3=2.51*nu(rho,mu)*math.sqrt(L)/(D*math.sqrt(2*g*D*hf))
    return d1*math.log10(d2+d3)
  except ValueError:
    print("Oops!  That was no valid number.  Try again...")

def hfb(g, Ht, zo, K, V):
  """
  Friction loses from Bernoulli equation
  """
  try:
    # Total minor losses
    het = he(g,sum(K),V)
    #for i in K:
    #  het += he(g,i,V)
    return Ht-zo-het
  except ValueError:
    print("Oops!  That was no valid number.  Try again...")


#def Htot(zi, zo, he, hf):
#  """
#  Total energy from the Bernoulli equation
#  """
#  try:
#    return zo-zi+he+hf
#  except ValueError:
#    print("Oops!  That was no valid number.  Try again...")

def HPu(E1, E2, he, hf, ht):
  """
  Total head energy delivered by a pump from the Bernoulli equation
  """
  try:
    return E2-E1+he+hf+ht
  except ValueError:
    print("Oops!  That was no valid number.  Try again...")

def HTu(E1, E2, he, hf, ht):
  """
  Total head energy extracted by a turbine from the Bernoulli equation
  """
  try:
    return E1-E2-he-hf+hp
  except ValueError:
    print("Oops!  That was no valid number.  Try again...")


def pot(US, eta, Q, H, g, rho):
  """
  Nominal system power
  """
  try:
    if US=='IS':
      return H*Q*rho*g/eta
    else:
      return (H*Q*rho*g/eta)/550. # transforming lb.ft/s to Hp
  except ValueError:
    print("Oops!  That was no valid number.  Try again...")

def head(eta, Q, P, g, rho):
  """
  Estimate the pump/turbine head
  """
  try:
      return P*eta/(Q*g*rho) 
  except ValueError:
    print("Oops!  That was no valid number.  Try again...")


def f_dw(g, hf, L, D, V):
  """
  Friction factor from Darcy-Weisbach equation
  """
  try:
    return hf*D*2*g/((V**2)*L)
  except ValueError:
    print("Oops!  That was no valid number.  Try again...")


def f_fp(g, ks, rho, mu, D, V):
  """
  Estimation of the friction factor using the fix point iteration method in the Colebrook-White equation.
  """

  try:
    # Calculate the Re
    Rey = Re(rho, mu, D, V)
    
    if Rey <= 2200:
      return 64./Rey
    else:
      f = Fi # Initialize f
      fl = []
      diffl = []
      while True:
        fl.append(f)
        # Estimate f2
        d1 = ks/(3.7*D)
        d2 = 2.51/(Rey*math.sqrt(f))
        f2 = (-2.*math.log10(d1+d2))**(-2.)
    
        diff = f2-f
        diffl.append(diff)
        if abs(diff)<=ERROR:
          break
        f = f2
      
      return {'f':f, 'f_list':fl, 'df':diffl}    
      
  except ValueError:
    print("Oops!  That was no valid number.  Try again...")

def f_fp2(g, ks, rho, mu, D, E1, E2, hp, ht, L, SK):
  """
  Estimation of the friction factor using the fix point iteration method in the Colebrook-White equation when velocity is unknown
  """

  try:
    f = Fi # Initialize f
    fl = []
    Vl = []
    hfrl = []
    while True:
      V = math.sqrt(2*g*(E1-E2 + hp - ht)*((f*(L/D)+SK)**(-1.))) # Calculate the velocity
      Rey = Re(rho, mu, D, V) # Calculate the Re
      hfr = hf(g,f,L,D,V) # Calculate friction losses
      fl.append(f)
      Vl.append(V)
      hfrl.append(hfr)
      if Rey <= 2200:
        f2 = 64./Rey
      else: 
        # Estimate f2
        d1 = ks/(3.7*D)
        d2 = 2.51/(Rey*math.sqrt(f))
        f2 = (-2.*math.log10(d1+d2))**(-2.)
    
      if abs(f2-f)<=ERROR:
        break
      f = f2
      
    return {'f':f, 'V':V, 'fl':fl, 'Vl':Vl, 'hfrl':hfrl}    
      
  except ValueError:
    print("Oops!  That was no valid number.  Try again...")


def f_nr(g, ks, rho, mu, D, V):
  """
  Estimation of the friction factor using the Newton-Raphson  method in the Colebrook-White equation.
  """

  try:
    # Calculate the Re
    Rey = Re(rho, mu, D, V)
    
    if Rey <= 2200:
      return 64./Rey
    else:
      f = Fi # Initialize f
      x = 1./math.sqrt(f)
      fl = []
      diffl = []
      while True:
        fl.append(f)
        # Estimate fx
        d1 = ks/(3.7*D)
        d2 = 2.51*x/Rey
        fx = -2.*math.log10(d1+d2)

        # Estimate dfx 
        d1 = ks/(3.7*D)
        d2 = 2.51*x/Rey
        d3 = 2.51/Rey
        dfx = (-2/math.log(10))*(d3/(d1+d2))

        # Newton-Raphson
        x2 = x - (fx - x)/(dfx - 1)

        diff = x2-x
        diffl.append(diff)
        if abs(diff)<=ERROR:
          break
        x = x2
        f = 1./(x**2)
      
      return {'f':f, 'f_list':fl, 'df':diffl}    
      
  except ValueError:
    print("Oops!  That was no valid number.  Try again...")

def f_nr2(g, ks, rho, mu, D, E1, E2, hp, ht, L, SK):
  """
  Estimation of the friction factor using the Newton-Raphson  method in the Colebrook-White equation when velocity is unknown
  """

  try:
    f = Fi # Initialize f
    x = 1./math.sqrt(f)
    fl = []
    Vl = []
    hfrl = []
    while True:
      V = math.sqrt(2*g*(E1-E2 + hp - ht)*((f*(L/D)+SK)**(-1.))) # Calculate the velocity
      Rey = Re(rho, mu, D, V) # Calculate the Re
      hfr = hf(g,f,L,D,V) # Calculate friction losses
      fl.append(f)
      Vl.append(V)
      hfrl.append(hfr)
      if Rey <= 2200:
        x2 = math.sqrt(64./Rey)
      else: 
        # Estimate fx
        d1 = ks/(3.7*D)
        d2 = 2.51*x/Rey
        fx = -2.*math.log10(d1+d2)

        # Estimate dfx 
        d1 = ks/(3.7*D)
        d2 = 2.51*x/Rey
        d3 = 2.51/Rey
        dfx = (-2/math.log(10))*(d3/(d1+d2))

        # Newton-Raphson
        x2 = x - (fx - x)/(dfx - 1)

      if abs(x2-x)<=ERROR:
        break
      x = x2
      f = 1./(x**2)
    
    return {'f':f, 'V':V, 'fl':fl, 'Vl':Vl, 'hfrl':hfrl}    
      
  except ValueError:
    print("Oops!  That was no valid number.  Try again...")


def gravity(US):
  """
  Return the gravity acceleration depend on the unit system
  """
  if US=='IS':
    return 9.81
  else:
    return 32.2

 
if __name__ == '__main__':

  g = 9.81
  rho = 998.2
  ks = 1.5e-6
  D = 0.293
  E2=0
  E1 = 43.5
  hb = 0
  ht = 0
  mu = 1.005e-3
  L = 730
  SK = 11.8

  
  res = f_fp2(g, ks, rho, mu, D, E1, E2, hb, ht, L, SK)
  print(res)
  res = f_nr2(g, ks, rho, mu, D, E1, E2, hb, ht, L, SK)
  print(res)
  Q = 0.042
  V = Vc(Q,D)
  #print(V)
  #mu = nu*rho
  #
  #print(Re(rho,mu,D,V))
  f = f_fp(g, ks, rho, mu, D, V)
  print(f)

  f = f_nr(g, ks, rho, mu, D, V)
  print(f)




