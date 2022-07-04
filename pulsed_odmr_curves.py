import numpy as np
import matplotlib.pyplot as plt
import os
import matplotlib
matplotlib.use('TkAgg')


dir = 'C:\\Data\\OPX_Datadump\\20220425'
path = [dir+'\\'+x for x in os.listdir(dir) if 'npz' in x and 'odmr' in x]


fig = plt.figure()
for entr in path:
    array = np.load(entr)['arr_0']
    plt.plot(array[0]+2.77e9, array[1] / np.mean(array[1, 0:int(1 / 7 * len(array[1]))]),
             label=f'{int(entr[entr.find("r_") + 2:-6])}ns')
plt.legend()
plt.show()
