
import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np



data = np.load('lib/messung.npz')['arr_0']

plt.plot(data[0], data[1])
plt.show()