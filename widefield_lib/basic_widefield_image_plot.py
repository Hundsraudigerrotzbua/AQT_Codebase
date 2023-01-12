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

roi_size = 1024  # pixels

work_dir = 'D:\\Widefield\\Daten\\telescope_max_focus\\'
file_name = '9_point_odmr_12012023_long'
path = work_dir + file_name + '.raw'
n_f = 9
n_avg = 1500


def sweep(path):
    chunk_size = roi_size ** 2
    imgMWON_sum = np.zeros((n_f, 1024, 1024))
    imgMWOFF_sum = np.zeros((n_f, 1024, 1024))
    for f in range(0,n_f):
        print(f'Reading in step {f} with MW on')
        for n in range(0, n_avg):
            print(f"{(n+1)*(f+1)}", end='\r', flush=True)
            shift = 2*f*n_avg*chunk_size + n*chunk_size
            imgMWON_sum[f, :, :] += np.fromfile(path, dtype='uint16', sep="", count=chunk_size,
                                             offset=shift*2).reshape(1024,
                                                                   1024).astype(int)  # mal 2, da jeder Eintrag 16 statt 8 bit is
        print(f'Reading in step {f} with MW off')
        for n in range(n_avg, 2*n_avg):
            print(f"Frame Nr. {(n+1)*(f+1)}", end='\r', flush=True)
            shift = 2*f * n_avg * chunk_size + n * chunk_size
            imgMWOFF_sum[f, :, :] += np.fromfile(path, dtype='uint16', sep="", count=chunk_size,
                                                offset=shift * 2).reshape(1024,
                                                                          1024).astype(int)  # mal 2, da jeder Eintrag 16 statt 8 bit is
    np.savez(f'{file_name}.npz', mw_on=imgMWON_sum, mw_off=imgMWOFF_sum)
    return imgMWON_sum, imgMWOFF_sum

if not os.path.exists(f'D:/QM_OPX/widefield_lib/{file_name}.npz'):
    print(f'No data found in D:/QM_OPX/widefield_lib/{file_name}.npz')
    print(f'Reading new data...')
    mw_on, mw_off = sweep(path)
    print(f'Data read out and saved to D:/QM_OPX/widefield_lib/{file_name}.npz')
else:
    print(f'Found data: D:/QM_OPX/widefield_lib/{file_name}.npz')
    mw_on = np.load(f'D:/QM_OPX/widefield_lib/{file_name}.npz')['mw_on']
    mw_off = np.load(f'D:/QM_OPX/widefield_lib/{file_name}.npz')['mw_off']
fig, (ax, ax2) = plt.subplots(2,1)
divider = make_axes_locatable(ax2)
cax = divider.append_axes('right', size='5%', pad=0.05)
bin_width = 1
mw= mw_on/mw_off#1 - mw_on/mw_off
y = [x.reshape(roi_size//bin_width, bin_width, roi_size//bin_width, bin_width).sum(3).sum(1) for x in mw]

x_idx = [int(x) for x in np.array([50])/64 * y[0].shape[0]] + [420, np.random.randint(1024), np.random.randint(1024), np.random.randint(1024), np.random.randint(1024)]
y_idx = [int(x) for x in np.array([10])/64 * y[0].shape[1]] + [420, np.random.randint(1024), np.random.randint(1024), np.random.randint(1024), np.random.randint(1024)]
for x_i, y_i in zip(x_idx, y_idx):
    odmr = np.array([k[x_i, y_i] for k in y])
    ax.plot(odmr, zorder=1)
    ax2.plot(x_i, y_i, 'o', zorder=2)
    ax.set_xlabel('Frequency [GHz]')

while 1:
    for idx in range(0, n_f):
        im = ax2.imshow((1-y[idx])*100, zorder=1, vmin=0, vmax=5)
        fig.colorbar(im, cax=cax, orientation='vertical')
        li = ax.axvline(idx, label=f'{idx}', zorder=2)
        plt.pause(0.5)
        im.remove()
        li.remove()
plt.show()