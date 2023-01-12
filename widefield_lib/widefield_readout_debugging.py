import numpy as np
import matplotlib.pyplot as plt
import datetime
import matplotlib
import os
from mpl_toolkits.axes_grid1 import make_axes_locatable
from Archiv.OLD_CODE_BASE_BEFORE_DATA_STRUCTURE.lib.utilities import save_data_to_json as save
#matplotlib.use("TkAgg")

font = {
    'size' : 18}
matplotlib.rc('font', **font)

# TODO: Alle Daten eines Ordners durchplotten

roi_size = 1024  # pixel
chunk_size = roi_size ** 2

work_dir = 'D:\\Widefield\\Daten\\telescope_max_focus\\'
file_name = 'odmr_no_reference'
#file_name = 'beeg_data_minus3dBm_1'
path = work_dir + file_name + '.raw'
n_f = 3
n_avg = 1000
#data = np.fromfile(path, dtype='uint16', sep="")
#np.savez(f'{file_name}.npz', data=data)
data = np.load(f'D:/QM_OPX/widefield_lib/{file_name}.npz')['data']
f1 = data.reshape(1024, 1024, 3000)
fig, ax = plt.subplots(1,1)
for frame in np.arange(0, 3000, 50):
    idx=frame*chunk_size
    im = data[idx:idx+chunk_size].reshape(roi_size, roi_size)
    plt.title(f'{frame}')
    image = ax.imshow(im)
    plt.pause(0.1)
    image.remove()
