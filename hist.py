import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

grf = np.genfromtxt('/scratch/chaste_test_output/a_hist.csv', delimiter=',')

plt.figure(1, figsize=(16, 10), dpi=72)


plt.subplot(1, 1, 1)

mu, sigma = 0, 1

plt.axis([-3*sigma, 3*sigma, 0, 0.5])
plt.grid(True)
n, bins, patches = plt.hist(grf, 50, normed=1, facecolor='green', alpha=0.75)

# add a 'best fit' line
y1 = mlab.normpdf(bins, mu, sigma)
l1 = plt.plot(bins, y1, 'b--', linewidth=5)

plt.show()
