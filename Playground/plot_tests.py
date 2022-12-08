from lib.plot_lib import *
from lib.data_handler import file_grabber, path_grabber
import os
import numpy as np
import matplotlib.pyplot as plt
font = {#'family': 'normal',
    # 'weight' : 'bold',
    'size': 15}
matplotlib.rc('font', **font)


#path = path_grabber('20221207', 'hahn', 12)
#file = file_grabber(path, meas_id=3)[0][0][0]
path = ['D:\\QM_OPX\Data\\2022\\11\\20221118\\46_20221118_16-20-19_rabi__check_if_buffer_averaging_jumps_too']
file = file_grabber(path)[0]

fig, ax = plt.subplots(1,1)#plot_ramsey(file['times'], file['counts'], file['counts2'])
for i in range(4,12):
    ax.plot(file[i][0]['times'], file[i][0]['counts'], label=f'ID {i}')
plt.legend()
plt.show()