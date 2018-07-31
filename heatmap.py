import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

grf = np.genfromtxt('/scratch/chaste_test_output/a_gaussian.csv', delimiter=',')

plt.figure(1, figsize=(24, 10), dpi=72)


plt.subplot(1, 2, 1)
plt.imshow(grf, interpolation='none', origin='lower', extent=[0, 1, 0, 1])


# Generate N normally-distributed random numbers
mu, sigma = 0, 1

plt.subplot(1, 2, 2)
plt.axis([-3*sigma, 3*sigma, 0, 0.5])
plt.grid(True)
n, bins, patches = plt.hist(grf.reshape(np.prod(grf.shape), 1), 50, normed=1, facecolor='green', alpha=0.75)

# add a 'best fit' line
y1 = mlab.normpdf(bins, mu, sigma)
l1 = plt.plot(bins, y1, 'b--', linewidth=5)

plt.show()
