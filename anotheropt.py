import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fan_curves2 import FANCURVE, FANCON, SCAL, wgtokpa
g = 9.81
epsilon = 45e-6 # carbon steel
rho = 1.225 # TODO change this
gamma = rho * g
R = 0.287 # kJ/kg/K
viscosity = 1.81e-5

def spec_v(T, P): return R * T / P

def dw(D, v, visc=viscosity):
   Re = v * D / visc
   return 1 / (-1.8 * np.log10( (epsilon / D)**1.11 / 3.17 + 6.9 / Re))**2

def h_major(L, D, mdot, visc=viscosity):
    v = mdot / rho / (np.pi / 4 * D ** 2)
    f= dw(D, v, visc)
    h = f * L * v ** 2 / 2 / g
    print 'FRICTION ', h, f, v, D
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
L_1 = 20.
L_2 = 10.
L_3 = 10.
L_4 = 20.
def work(DV=[265., 1., 1., 1., 1., .25, 1., 2.], t3a=293.15, ql=100, t1a=275., cp=1.005, tho=310., p1a=600., n_s_comp=.9, n_s_turb=.9, returnall=False):
#def work(tlo=265., mdotHElow=1., mdot=1., LHEd=1., HHEd=1., HPd = .25, LPd=1., t3=20., ql=0.6, t1=275., cp=1.005, tho=310., ):
   tlo = 250.
   mdot = DV[0]
   HPd = 1.
   LPd = 0.3
   r = DV[1]

   k = 1.4

   # I have a lot of statements here to catch bad DV values.
   # I would like to explicitly add these things as constraints later, though
   # some things (like negative pressure) can only be caught during the calculations.
   t4b = t1a - ql/cp/mdot
   p4b = p1a * (t4b / t1a) **(k/(k-1))
   p4a = p4b + h_major(L_4, LPd, mdot) * gamma
   t4a = t4b * (p4a / p4b) ** ((k-1)/k)
   p1b = p1a - h_major(L_1, LPd, mdot) * gamma 
   t1b = t1a * (p1b / p1a) ** ((k-1)/k)
   p2a = p1b * (r)
   t2a = t1b * (p2a / p1b) ** ((k-1)/k)
   p2b = p2a - h_major(L_2, HPd, mdot) * gamma
   w12 = cp*(t2a - t1b) * mdot / n_s_comp # kJ
   #print 't2a, p2b, p2a, k', t2a, p2b, p2a, k
   t2b = t2a * (p2b/p2a) ** ((k-1)/k)
   qh = cp * (t2b - t3a) * mdot
   p3a = p2b * (t3a / t2b) ** (k/(k-1))
   p3b = p3a -  h_major(L_3, HPd, mdot) * gamma
   t3b = t3a * (p3b / p3a) ** ((k-1)/k)
   w34 = cp * (t3b - t4a) * mdot
   #print 'qh tho t3a', qh, tho, t3a
   print 'tdiff hi ', (tho - t3a), 'tdiff low', (t1a - tlo)
   mdotHEhigh = qh / (cp * (tho - t3a))
   mdotHElow = ql / (cp * (t1a - tlo))
   #print 'mdotHElow, ql, t1a, tlo ',mdotHElow, ql, t1a, tlo

   dph = h_major(10., HPd, mdotHEhigh)
   dpl = h_major(40., LPd, mdotHElow)
   print 'dph, HPd, mdotHEhigh, (tho - t3a), qh', dph, HPd, mdotHEhigh, (tho - t3a), qh
   print 'dpl, LPd, mdotHElow, (t1a - tlo), ql', dpl, LPd, mdotHElow, (t1a - tlo), ql


   vh = (spec_v(t3a, 100) + spec_v(tho, 100)) / 2
   #print 'vh, mdotHEhigh, qh, t2b, r' , vh, mdotHEhigh, qh, t2b, r
   #print 'vhdot ', vh * mdotHEhigh / 1000 ; quit()
   wh = FANCURVE(vh * mdotHEhigh * 35.3147 / 1000, dph / SCAL / wgtokpa)  * SCAL ** (2./3) * 1 / 0.7457 # HP to kW
   #print 'wh, vh * mdotHEhigh * 35.3147 / 1000, dph / SCAL / wgtokpa ', wh, vh * mdotHEhigh * 35.3147 / 1000, dph / SCAL / wgtokpa
   #if wh< 0: return -1 * wh * 100000
   #if wh< 0: print '*** ', tho, t3a, dph / SCAL / wgtokpa, vh * mdotHEhigh / 1000, wh ; quit()

#   wh = mdotHEhigh * cp * (tho - t3a) - qh
   #wl = mdotHElow * cp * (tlo - t4b) + ql

   vl = (spec_v(tlo, 100) + spec_v(t4a, 100)) / 2
   wl = FANCURVE(vl * mdotHElow * 35.3147 / 1000, dpl / SCAL / wgtokpa)  * SCAL ** (2./3) * 1 / 0.7457 # HP to kW
   print 'wl, vl * mdotHElow * 35.3147 / 1000, dpl / SCAL / wgtokpa', wl, vl * mdotHElow * 35.3147 / 1000, dpl / SCAL / wgtokpa

   #print '====== ', tlo > t1a
   print '----> , ', wl < 0 #or tlo > t1a or mdot < .2 or t4b < 0
   if (
   p3b / p4a > r or
   #qh > 2000 or  # why is this here?
   #mdotHEhigh < 0.2 or

   # Diameter maximum / miniums
   #LPd < 0 or HPd < 0 or 
   #LPd > 10. or
   #HPd > 1 or

   wh < 0 or

   tlo > t1a or
   mdot < .2 or t4b < 0 or
   p4b < 5 or
   p4a < 5 or
   p3a < 5 or
   p3b < 5 or
   p1b < 5 or
   t3b < 0 or
   t4a < 0 or
   r< 1 or
   mdotHElow < 0 or
   wl < 0 or
   p2b < 50 or
   p2a < 0 or
   t1b < 0 or
   t2a < 0 or
   #tlo < 200 or
   p2b < 50 or 
   t2b < 0): return 9999999
   if w12 < 0: print 'w12<0: ', t2a, t1b, t1a, mdot, n_s_comp, cp ; quit()
   if t2a < t1b: print 't2a < t1b: ', t2a, t1b, p2a, p1b ; quit()


   wnet = w12 + wh + wl - w34 # Wnet
   if wnet <0:  
                print '---'
                print qh
                print '---'
                print DV
                print 'wnet<0 ', t2a, t1b, t3b, t4a
                print p1b, p2a, p3b, p4a
                print p4b, p1a, mdot, LPd, h_major(L_1, LPd, mdot) * gamma
                print w12, w34 ; quit()
   if returnall: return [qh, t2b - t3a , ql, (t1a - t4b + t1a - tlo) / 2, vl * mdotHElow / 1000, dpl, vl, mdotHElow]
   #if returnall: print qh, wh, tho, t3a, mdotHEhigh ; quit() ; return [wh, (t2b - t3a + t3a - tho ) / 2, wl, (t4b - t1a + t1a - tlo) / 2]
   return wnet

#work = np.vectorize(work)
#W = np.arange(0, 250, .1)
#plt.plot(W, W/work(ql=W))
#plt.ylabel('COP', size=12)
#plt.xlabel(r'$\dot{Q}_L$ (kW)', size=12)
#plt.tight_layout()
#plt.savefig('COP.pdf')

# Optimization
x0 = np.array([1., 15.])
w0 = work(x0)
from scipy.optimize import minimize
con = {'type': 'ineq', 'fun': lambda x:100* np.min(x),} # non-negativity constraint
x = minimize(work, x0, method="Powell", constraints=con, options={'maxiter':100000, 'disp':True, 'iprint':1}).x
for _ in range(20): x = minimize(work, x, method="Powell", constraints=con, options={'maxiter':100000, 'disp':True, 'iprint':1}).x

w = work(x)
p = work(x, returnall=True)
print 'mdot = ', x[0], ' kg/s'
print 'HPd = ', 1., ' m'
print 'LPd = ', 10., ' m'
print 'pressure ratio is ', x[1]
print 'Work is ', w, ' kW'
print 'baseline is ', w0, ', kW'
print ' '
print 'Heat Exchanger Area Requirements: (assume k=385.0 W/mK and x = .05 m)'
U = .358 / .05 # kW / m^2 / K
qh = p[0]
dth = p[1]
ql = p[2]
dtl = p[3]
print ' --- ' 
print 'U ', U , 'qh ', qh, ', DTh ', dth, ', ql ', ql, ', DTl', dtl, ' vdt', p[4], 'pl ', p[5], ' vl', p[6], ' mdotL ', p[7]
print ' --- ' 
print 'High-temperature heat exchanger area: ', qh / dth / U, ' m^2'
print 'Low-temperature heat exchanger area: ', ql / dtl / U, ' m^2'

