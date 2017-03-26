import matplotlib
import matplotlib.pyplot as plt
import numpy as np

y = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
x = np.arange(10)
fig = plt.figure()
ax = plt.subplot(111)
ax.plot(x, y,'ro')
plt.title('Legend inside')
ax.legend()

fig.savefig('plot.png')