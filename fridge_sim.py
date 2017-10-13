import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
air_dat = pd.read_excel('./air_props.xlsx')
def pr_to_temp(p_r):
   return np.interp(p_r, air_dat.P_r, air_dat['T'])

def temp_to_pr(temp):
   return np.interp(temp, air_dat['T'], air_dat.P_r)

def work(t3=20., ql=0.6, t1 = 275., tho=310., tlo=265., cp = 1.005, mdotHElow=1., mdotHEhigh=1., mdot=1.):
   t3 += 273
   k = 1.4

   t4 = t1 - ql/cp
   w34 = cp * (t3 - t4)
   
   pr1 = temp_to_pr(t1)
   pr2 = pr1 * (t3/t4) ** (k/(k-1))
   t2 = pr_to_temp(pr2)
   print ql, t2

   w12 = cp*(t2 - t1) # kJ/kg
   qh = cp * (t2 - t3)
   #print qh, w12, w34, ql
   if abs(qh - (w12+ql-w34)) > .3: return np.nan, np.nan
   #if w12 + qh + ql - w34 <0: return np.nan, np.nan

   wh = cp * (tho - t3) - qh
   wl = cp * (tlo - t4) + ql
   return ql / (w12 + wh + wl - w34)
   #return w12 + wh + wl - w34#, qh
   #return qh

work = np.vectorize(work)
T = np.arange(10, 30)
Q = np.arange(0, 80)
plt.plot(Q, work(ql=Q), label='Air') 
plt.plot(Q, work(ql=Q, cp=0.844), label='CO2') 
plt.plot(Q, work(ql=Q,  cp=2.19), label='Ammonia') 
plt.legend()
plt.xlabel('qh (kW)')
plt.ylabel('COP')
plt.savefig('./T_conts.pdf')
