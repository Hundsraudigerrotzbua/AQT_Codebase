from lib.plot_lib import *
from lib.data_handler import file_grabber, path_grabber
import os
import numpy as np
import matplotlib.pyplot as plt
font = {#'family': 'normal',
    # 'weight' : 'bold',
    'size': 15}
matplotlib.rc('font', **font)

path = path_grabber("20221210", file_id=2)
entries = file_grabber(path)
file = [x for entry in entries for x in entry]
#file = entries[0]

#file = entries[0] + entries[1]
#file = file[:-1] # because the script crashed and the last iteration has low counts


fig, ax = plt.subplots(1,1)#plot_ramsey(file['times'], file['counts'], file['counts2'])
for f in file:
    ax.plot(f[0]['times']*4, f[0]['counts'], label=f'ID {int(f[1].split("_")[0])}', linewidth=3, alpha=int(f[1].split("_")[0])/len(file))
ax.legend(ncol=len(file)//2)
ax.set_xlabel(r'Pulsetime $\tau$ [ns]')
ax.set_ylabel(r'Total summed counts [arb. u.]')
ax.grid()
for side in ax.spines.keys():
    ax.spines[side].set_linewidth(3)
ax.tick_params(axis='x', direction='in', length=8, width=3)
ax.tick_params(axis='y', direction='in', length=8, width=3)
ax.set_title('Rabi Measurements to compare OPX+')
plt.minorticks_on()
ax.xaxis.set_minor_locator(AutoMinorLocator(2))
ax.yaxis.set_minor_locator(AutoMinorLocator(2))
plt.grid(which='major', linewidth=1)
plt.grid(which='minor', linewidth=1, linestyle='--')
plt.show()
