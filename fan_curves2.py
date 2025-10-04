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
Z = scipy.interpolate.Rbf(vmf, press, pwrlist, function='thin-plate', fill_value = 9999.)
#FANCON = scipy.interpolate.Rbf(
#         [0., 2., 6., 8., 10., 12., 14., 16.],
#         [0., .14, .5, .7, 1.2, 1.5, 2.2, 2.5], fill_value="extrapolate", function='cubic')
         #fill_value=2.5.)
FANCURVE = Z
SCAL = 50.
wgtokpa = 1. / 4.01865
def FANCON(v): return SCAL * wgtokpa * (0.00792775 * v**2 + 0.03428444 * v + 0.00830688)
if __name__=='__main__':
   z = Z(X,Y) * (SCAL ** 2./3.)
   c = plt.contour(X, Y * SCAL * wgtokpa, z, colors='k')
   #c = plt.contour(X, Y * SCAL * wgtokpa, z, colors='k', levels = np.array([1, 2, 3, 5, 7.5, 10, 15]) * SCAL **(2./3.))
   plt.clabel(c)
   plt.savefig('t1.pdf')
   plt.contourf(X, Y * SCAL * wgtokpa, z, alpha=0.4, cmap=plt.cm.coolwarm)
   #c = plt.contour(X * 400, Y * (400 ** 2./3.), Z(X,Y) * (400 ** 2./3.), levels=[1, 2, 3, 5, 7.5, 10, 15], colors='k')
   plt.ylim(0, np.max(Y * SCAL ) * wgtokpa)
   print 'probe1'
   print 'probe2'
   plt.plot(np.arange(0, 20), FANCON(np.arange(0, 20)), ls='--')
   plt.ylabel('Pressure Difference (kPa)')
   #plt.ylabel('Pressure Difference (inches w.g.)')
   plt.xlabel('Volumetric Flow Rate (1000 cfm)')
   plt.title('Power (HP)')
   plt.text(6.5, 400, "Do not design to the left of this line", rotation = 60)
   plt.savefig('done.png')
