import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
air_dat = pd.read_excel('./air_props.xlsx')
def pr_to_temp(p_r):
   return np.interp(p_r, air_dat.P_r, air_dat['T'])

def temp_to_pr(temp):
   return np.interp(temp, air_dat['T'], air_dat.P_r)

def work(t3=20., ql=0.6, t1 = 275., tho=310., tlo=265.):
   t3 += 273
   cp = 1.005 # kJ/kg/k
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
#fig, ax1 = plt.subplots(2, 2, sharex=True, sharey=True, figsize=(10,10))
#for i in range(1,5):
#   d, r = divmod(i-1, 2)
#   wn, qh = work(t3=T, ql=.6 * i)
#   ax1[d, r].plot(T, wn, label='net work')
#   ax1[d, r].plot(T, qh, label='cooling load')
#   ax1[d,r].legend()
#   ax1[d,r].set_title("ql = %f kW"%(.6*i))
plt.plot(Q, work(t3=15, ql=Q), label='T3=15') 
plt.plot(Q, work(t3=20, ql=Q), label='T3=20') 
plt.plot(Q, work(t3=20, ql=Q), label='T3=20') 
plt.plot(Q, work(t3=25, ql=Q), label='T3=25') 
#plt.plot(T, work(ql=Q), label='') 
#plt.plot(T, work(ql=Q), label='ql=20') 
plt.legend()
#ax1[0,0].set_ylabel('Work (kW)')
#ax1[1,0].set_ylabel('Work (kW)')
#ax1[1,1].set_xlabel('Ambient Temperature (K)')
#ax1[1,0].set_xlabel('Ambient Temperature (K)')
#plt.savefig('effs.pdf')
plt.xlabel('qh (kW)')
#plt.ylabel('Qh (kW)')
plt.ylabel('COP')
plt.show()
