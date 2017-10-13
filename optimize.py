import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
air_dat = pd.read_excel('./air_props.xlsx')
def pr_to_temp(p_r):
   return np.interp(p_r, air_dat.P_r, air_dat['T'])

def temp_to_pr(temp):
   return np.interp(temp, air_dat['T'], air_dat.P_r)

''' Calculate the work needed to operate the system in steady-state.

Design Variable
tlo - outlet temperature of low-temp heat exchanger (K)
mdotHElow - mass flow rate of low temperature heat exchanger (kg/s)
mdot - Brayton cycle mass flow rate (kg/s)
LHEd - low-temp heat exchanger diameter (inches)
HHEd - high-temperature heat exchanger diameter (inches)
HPd - Brayton cycle high-pressure diamter (inches)
LPd - Brayton cycle low-pressure diameter (inches)

State variables
t1 - temperature inside the cooled space (K)
tho - maximum outlet temperature of high-temperature heat exchanger (K)
t3 - environmental/ambient temperature (C)
ql - cooling load (kW)
cp - kj/kg/K
'''
def work(DV=[265., 1., 1., 1., 1., .25, 1.], t3=20., ql=100, t1=275., cp=1.005, tho=310., ):
#def work(tlo=265., mdotHElow=1., mdot=1., LHEd=1., HHEd=1., HPd = .25, LPd=1., t3=20., ql=0.6, t1=275., cp=1.005, tho=310., ):
   tlo = DV[0]
   mdotHElow = DV[1]
   mdot = DV[2]
   LHEd = DV[3]
   HHEd = DV[4]
   HPd = DV[5]
   LPd = DV[6]

   t3 += 273
   k = 1.4
   t4 = t1 - ql/cp/mdot

   w34 = cp * (t3 - t4) * mdot
   
   pr1 = temp_to_pr(t1)
   pr2 = pr1 * (t3/t4) ** (k/(k-1))
   t2 = pr_to_temp(pr2)

   w12 = cp*(t2 - t1) * mdot # kJ
   qh = cp * (t2 - t3) * mdot

   # sanity check
   if abs(qh - (w12+ql-w34)) > .3: raise Exception("abs(qh - (w12+ql-w34)) > .3. \nqh = %f\nw12=%f\nql=%f\nw34=%f"%(qh,w12,ql,w34))

   mdotHEhigh= qh / (cp * (tho - t3))

   wh = mdotHEhigh * cp * (tho - t3) - qh
   wl = mdotHElow * cp * (tlo - t4) + ql
   wnet = w12 + wh + wl - w34 # Wnet
   return wnet

# Optimization
x0 = np.array([265., 1., 1., 1., 1., .25, 1.])
from scipy.optimize import minimize
con = {'type': 'ineq', 'fun': lambda x:100* np.min(x),}
x = minimize(work, x0, method="COBYLA", constraints=con).x

print 'tlo = ', x[0]
print 'mdotHElow', x[1]
print 'mdot = ', x[2]
print 'LHEd = ', x[3]
print 'HHEd = ', x[4]
print 'HPd = ', x[5]
print 'LPd = ', x[6]
print 'Work is ', work(x)

