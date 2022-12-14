from lib.plot_lib import *
from lib.data_handler import file_grabber, path_grabber
import os
import numpy as np
import matplotlib.pyplot as plt
font = {#'family': 'normal',
    # 'weight' : 'bold',
    'size': 15}
matplotlib.rc('font', **font)


path = path_grabber('20221212', 44)
file_arr = file_grabber(path)[0]
file_arr = [entry[0] for entry in file_arr if int(entry[1].split("_")[1])==1]

fig, ax = plt.subplots(1,1)
for idx in range(0, len(file_arr)):
    if idx%5 == 0:
        ax.plot(file_arr[idx]['times'] * 4, file_arr[idx]['counts'] / 1.5e6 / 600e-9, color='b', lw=4,
                alpha=idx / len(file_arr), label=f'{idx}/{len(file_arr)}')
        ax.plot(file_arr[idx]['times'] * 4, file_arr[idx]['counts2'] / 1.5e6 / 600e-9, color='r', lw=4,
                alpha=idx / len(file_arr))
ax.set_xlabel(r'Dephasing Time $\tau$ [ns]')
ax.set_ylabel(r'Counts [cps]')
ax.legend()
ax.grid()
for side in ax.spines.keys():
    ax.spines[side].set_linewidth(3)
ax.tick_params(axis='x', direction='in', length=8, width=3)
ax.tick_params(axis='y', direction='in', length=8, width=3)
ax.set_title('Ramsey')
plt.minorticks_on()
ax.xaxis.set_minor_locator(AutoMinorLocator(2))
ax.yaxis.set_minor_locator(AutoMinorLocator(2))
plt.grid(which='major', linewidth=1)
plt.grid(which='minor', linewidth=1, linestyle='--')

plt.show()
