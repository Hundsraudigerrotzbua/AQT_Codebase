import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
a = np.load('lib/counts_no_mw.npz')
b = np.load('lib/counts_mw.npz')

a_arr = a['arr_0']
a_arr = a_arr / np.linalg.norm(a_arr[350:450])
b_arr = b['arr_0']
b_arr = b_arr / np.linalg.norm(b_arr[350:450])

plt.plot(a_arr)
plt.plot(b_arr)
plt.show()