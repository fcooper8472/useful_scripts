import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

N = 1000000`

# Generate N normally-distributed random numbers
mu, sigma = 0, np.pi / np.sqrt(2)
x = mu + sigma*np.random.randn(N+1)

# Get the piecewise diff of the numbers
differences = np.diff(x)

# Scale by the necessary amount
scale_const = (x[N] - x[0]) / N
scaled_draws = differences - scale_const

print(x)
print(scaled_draws)

print(np.sum(scaled_draws))


# the histogram of the data
n, bins, patches = plt.hist(scaled_draws, 50, normed=1, facecolor='green', alpha=0.75)

# add a 'best fit' line
y1 = mlab.normpdf(bins, mu, np.pi)
l1 = plt.plot(bins, y1, 'r--', linewidth=1)

# y2 = mlab.normpdf(bins, mu, np.sqrt(2) * sigma)
# l2 = plt.plot(bins, y2, 'b--', linewidth=1)

plt.axis([-8, 8, 0, 0.2])
plt.grid(True)
plt.show()

