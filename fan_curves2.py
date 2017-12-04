import numpy as np
import scipy.interpolate
import matplotlib.pyplot as plt
hp = {0.5: 
        [[0., 8., 9.5], 
         [1., .12, 0]], 
      #.75: 
      #  [[0, 6, 9], 
      #   [1.2, .3, 0.]], 
      1.: 
        [[0, 14.], 
         [1.4, 0]], 
      #1.5: 
      #  [[0., 15.8], 
      #   [1.7, 0]], 
      2.: 
        [[0., 17], 
         [2.15, 0]], 
      3: 
        [[2, 16, 20.], 
         [2.4, .4, 0]], 
      5:
        [[5, 20., 23.5], 
         [2.5, 0.5, 0]], 
      7.5:
        [[11., 24], 
         [2.25, .5]]}

pwrs = sorted(hp.keys())
vmf, press, pwrlist = [], [], []
for pwr in pwrs:
  vmf += hp[pwr][0] 
  press += hp[pwr][1] 
  if len(hp[pwr][1]) != len(hp[pwr][0]): raise Exception('length mismatch in %f hp'%pwr)
  pwrlist += [pwr for _ in range(len(hp[pwr][0]))]
X, Y  = np.meshgrid(np.linspace(0, 26, 100), np.linspace(0, 2.5, 100))
Z = scipy.interpolate.Rbf(vmf, press, pwrlist, function='cubic', fill_value = 9999.)
FANCURVE = Z
if __name__=='__main__':
   c = plt.contour(X, Y, Z(X,Y), levels=[1, 2, 3, 5, 7.5, 10, 15], colors='k')
   plt.clabel(c)
   plt.contourf(X,Y, Z(X,Y), alpha=0.4, cmap=plt.cm.coolwarm)
   plt.ylabel('Pressure Difference (inches w.g.)')
   plt.xlabel('Volumetric Flow Rate (1000 cfm)')
   plt.title('Power (HP)')
   plt.show()
