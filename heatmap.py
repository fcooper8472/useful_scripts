import numpy as np
import matplotlib.pyplot as plt

grf = np.genfromtxt('/scratch/chaste_test_output/a_gaussian.csv', delimiter=',')

im = plt.imshow(grf, interpolation='bilinear', origin='lower', extent=[0, 1, 0, 1])

plt.show()