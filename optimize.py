import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
air_dat = pd.read_excel('./air_props.xlsx')
g = 9.81
epsilon = 45e-6 # carbon steel
rho = 1.225 # TODO change this
gamma = rho * g
def pr_to_temp(p_r):
   return np.interp(p_r, air_dat.P_r, air_dat['T'])

def temp_to_pr(temp):
   return np.interp(temp, air_dat['T'], air_dat.P_r)

def dw(D, v, visc):
   Re = v * D / visc
   return 1 / (-1.8 * np.log10( (epsilon / D)**1.11 / 3.17 + 6.9 / Re))**2

def h_major(L, mdot, D, visc=1.):
    v = mdot / rho / (np.pi / 4 * D ** 2)
    f= dw(D, v, visc)
    h = f * L * v ** 2 / 2 / g
    return h

''' Calculate the work needed to operate the system in steady-state.

Design Variable
tlo - outlet temperature of low-temp heat exchanger (K)
mdotHElow - mass flow rate of low temperature heat exchanger (kg/s)
mdot - Brayton cycle mass flow rate (kg/s)
LHEd - low-temp heat exchanger diameter (inches)
HHEd - high-temperature heat exchanger diameter (inches)
HPd - Brayton cycle high-pressure diamter (inches)
LPd - Brayton cycle low-pressure diameter (inches)
r - pressure ratio

State variables
t1 - temperature inside the cooled space (K)
p1 - pressure at exit of low-temp heat exchanger
tho - maximum outlet temperature of high-temperature heat exchanger (K)
t3a - environmental/ambient temperature (K)
ql - cooling load (kW)
cp - kj/kg/K
n_s_comp = compressor isentropic efficiency
n_s_turb = turbine " "
'''
L_HE_4 = 10 # m. length from HE to 4
L_1 = 20.
L_2 = 2.
L_3 = 2.
L_4 = 20.
def work(DV=[265., 1., 1., 1., 1., .25, 1., 2.], t3a=293.15, ql=100, t1a=275., cp=1.005, tho=310., p1a=400., n_s_comp=.9, n_s_turb=.9, returnall=False):
   print DV
#def work(tlo=265., mdotHElow=1., mdot=1., LHEd=1., HHEd=1., HPd = .25, LPd=1., t3=20., ql=0.6, t1=275., cp=1.005, tho=310., ):
   tlo = DV[0]
   mdotHElow = DV[1]
   mdot = DV[2]
   LHEd = DV[3]
   HHEd = DV[4]
   HPd = DV[5]
   LPd = DV[6]
   r = DV[7]

   k = 1.4


   t4b = t1a - ql/cp/mdot
   if mdot < .2 or t4b < 0: return 9999
   p4b = p1a * (t4b / t1a) **(k/(k-1))
   if p4b < 0: return 9999
   p4a = p4b + h_major(L_4, LPd, mdot) * gamma
   if p4a < 0: return 9999
   t4a = t4b * (p4a / p4b) ** ((k-1)/k)
   if t4a < 0: return 9999
   p1b = p1a - h_major(L_1, LPd, mdot) * gamma 
   if p1b <0: return 99999
   if r< 1: return 99999
   t1b = t1a * (p1b / p1a) ** ((k-1)/k)
   if t1b < 0: return 9999
   p2a = p1b * (r)
   if p2a < 0: return 9999
   t2a = t1b * (p2a / p1b) ** ((k-1)/k)
   if t2a < 0: return 9999
   if t2a < t1b: print 't2a < t1b: ', t2a, t1b, p2a, p1b ; quit()
   p2b = p2a - h_major(L_2, LPd, mdot) * gamma
   if p2b < 0: return 9999
   w12 = cp*(t2a - t1b) * mdot / n_s_comp # kJ
   if w12 < 0: print 'w12<0: ', t2a, t1b, t1a, mdot, n_s_comp, cp ; quit()
   if p2b < 0: return 999999
   t2b = t2a * (p2b/p2a) ** ((k-1)/k)
   if t2b < 0: return 999999
   qh = cp * (t2b - t3a) * mdot
   p3a = p2b * (t3a / t2b) ** (k/(k-1))
   if p3a < 0: return 999999
   p3b = p3a -  h_major(L_3, LPd, mdot) * gamma
   if p3b < 0: return 999999
   t3b = t3a * (p3b / p3a) ** ((k-1)/k)
   if t3b < 0: return 999999
   w34 = cp * (t3b - t4a) * mdot
   mdotHEhigh= qh / (cp * (tho - t3a))
   wh = mdotHEhigh * cp * (tho - t3a) - qh
   if mdotHEhigh < 0.2: return 9999
   wl = mdotHElow * cp * (tlo - t4b) + ql
   if mdotHElow < .2: return 9999
   if wl < 0: return 99999
   wnet = w12 + wh + wl - w34 # Wnet
   if wnet <0:  print 'wnet<0 ', w12, wh, wl, w34; quit()
   if returnall: return [wh, (t2b - t3a + t3a - tho ) / 2, wl, (t4b - t1a + t1a - tlo) / 2]
   return wnet
def cb(x): print x
# Optimization
x0 = np.array([265., 1., 1., 1., 1., .25, 1., 15.])
w0 = work(x0)
from scipy.optimize import minimize
con = {'type': 'ineq', 'fun': lambda x:100* np.min(x),} # non-negativity constraint
x = minimize(work, x0, method="COBYLA", constraints=con, options={'maxiter':100000, 'disp':True, 'iprint':1}).x

w = work(x)
p = work(x, returnall=True)
print 'tlo = ', x[0]-273, ' C'
print 'mdotHElow', x[1], 'kg/s'
print 'mdot = ', x[2], ' kg/s'
print 'LHEd = ', x[3], ' m'
print 'HHEd = ', x[4], ' m'
print 'HPd = ', x[5], ' m'
print 'LPd = ', x[6], ' m'
print 'pressure ratio is ', x[7]
print 'Work is ', w, ' kW'
print 'baseline is ', w0, ', kW'
print ' '
print 'Heat Exchanger Area Requirements: (assume k=385.0 W/mK and x = .005 m)'
U = .358 / .005 # kW / m^2 / K
qh = p[0]
dth = p[1]
ql = p[2]
dtl = p[3]
print ' --- ' 
print 'qh ', qh, ', DTh ', dth, ', ql ', ql, ', DTl', dtl
print ' --- ' 
print 'High-temperature heat exchanger area: ', qh / dth / U, ' m^2'
print 'Low-temperature heat exchanger area: ', ql / dtl / U, ' m^2'

