import numpy as np
import matplotlib.pyplot as plt
import os
import matplotlib
matplotlib.use('TkAgg')


dir = 'D:\QMTest\lib'
path = [dir+'\\'+x for x in os.listdir(dir) if 'npz' in x and 'rabi_' in x]


fig = plt.figure()
for entr in path:
    array = np.load(entr)['arr_0']
    plt.plot(array[0], array[1] / np.max(array[1]), label=f'{entr[entr.find("_") + 1:-4]}')
plt.legend()
plt.show()
