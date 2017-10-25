import numpy as np
import scipy.interpolate
import matplotlib.pyplot as plt
hp = {0.5: 
        [[0., 2., 6., 8., 9.5], 
         [1., .67, .25, .12, 0]], 
      .75: 
        [[0, 2, 4, 6, 8, 9], 
         [1.2, .85, .65, .3, .7, 0.]], 
      1.: 
        [[0, 1., 2., 4, 6, 8, 10., 12., 14.], 
         [1.4, 1.15, 1.13, .8, .7, .45, .3, .15, 0]], 
      1.5: 
        [[0., 1., 2., 6., 8., 10., 14., 15.8], 
         [1.7, 1.67, 1.4, .75, .63, .5, .09, 0]], 
      2.: 
        [[0., 2., 4, 6, 8, 10, 12, 14, 16., 17], 
         [2.15, 1.75, 1.38, 1., .9, .75, .6, .3, .08, 0]], 
      3: 
        [[2, 4, 6, 8, 10, 12, 14, 16, 17., 18, 20.], 
         [2.4, 1.6, 1.45, 1.25, 1.15, .9, .7, .4, (.4+.15)/2, .15, 0]], 
      5:
        [[5, 6., 7., 11., 16., 18., 20., 22., 23.5], 
         [2.5, 2.25, 2., 1.6, 1.05, .8, 0.5, .25, 0]], 
      7.5:
        [[9., 11., 14., 16., 18., 21., 24], 
         [2.5, 2.25, 1.85, 1.75, 1.3, 1., .5]]}

pwrs = sorted(hp.keys())
vmf, press, pwrlist = [], [], []
for pwr in pwrs:
  vmf += hp[pwr][0] 
  press += hp[pwr][1] 
  if len(hp[pwr][1]) != len(hp[pwr][0]): raise Exception('length mismatch in %f hp'%pwr)
  pwrlist += [pwr for _ in range(len(hp[pwr][0]))]
X, Y  = np.meshgrid(np.linspace(0, 26, 100), np.linspace(0, 2.5, 100))
Z = scipy.interpolate.Rbf(vmf, press, pwrlist, function='thin_plate')
c = plt.contour(X, Y, Z(X,Y), levels=pwrs, cmap=plt.cm.rainbow)
plt.clabel(c)
plt.colorbar()
plt.show()
