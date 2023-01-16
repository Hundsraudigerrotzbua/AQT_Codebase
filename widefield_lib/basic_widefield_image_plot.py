import numpy as np
import matplotlib.pyplot as plt
import datetime
import matplotlib
import os
from mpl_toolkits.axes_grid1 import make_axes_locatable

# matplotlib.use("TkAgg")

font = {
    'size': 18}
matplotlib.rc('font', **font)


# TODO: Alle Daten eines Ordners durchplotten

def sweep(path):
    chunk_size = roi_size ** 2
    imgMWON_sum = np.zeros((n_f, 1024, 1024))
    imgMWOFF_sum = np.zeros((n_f, 1024, 1024))
    for f in range(0, n_f):
        print(f'Reading in step {f} with MW on')
        for n in range(0, n_avg):
            print(f"{f * 2 * n_avg + n}", end='\r', flush=True)
            shift = 2 * f * n_avg * chunk_size + n * chunk_size
            try:
                imgMWON_sum[f, :, :] += np.fromfile(path, dtype='uint16', sep="", count=chunk_size,
                                                    offset=shift * 2).reshape(1024,
                                                                              1024).astype(
                    int)  # mal 2, da jeder Eintrag 16 statt 8 bit is
            except ValueError:
                print(f"MISSING DATA in Frame {f * 2 * n_avg + n}")
                pass
        print(f'Reading in step {f} with MW off')
        for n in range(n_avg, 2 * n_avg):
            print(f"Frame Nr. {f * 2 * n_avg + n}", end='\r', flush=True)
            shift = 2 * f * n_avg * chunk_size + n * chunk_size
            try:
                imgMWOFF_sum[f, :, :] += np.fromfile(path, dtype='uint16', sep="", count=chunk_size,
                                                     offset=shift * 2).reshape(1024,
                                                                               1024).astype(
                    int)  # mal 2, da jeder Eintrag 16 statt 8 bit is
            except ValueError:
                print(f"MISSING DATA in Frame {f * 2 * n_avg + n}")
                pass
    np.savez(f'{file_name}.npz', mw_on=imgMWON_sum, mw_off=imgMWOFF_sum)
    return imgMWON_sum, imgMWOFF_sum


roi_size = 1024  # pixels

work_dir = 'D:\\Widefield\\Daten\\telescope_max_focus\\'
f = np.array([2.68, 2.77, 2.87, 2.97, 3.07]) * 1e9
iteration_array = [f[i:i + 3] for i in np.arange(0, len(f), 3)]
for idx, f_vec_array in enumerate(iteration_array):
    n_f = len(f_vec_array)
    n_avg = 50
    file_name = f'camera_state_test_{idx}'
    path = work_dir + file_name + '.raw'

    if not os.path.exists(f'D:/QM_OPX/widefield_lib/{file_name}.npz'):
        print(f'No data found in D:/QM_OPX/widefield_lib/{file_name}.npz')
        print(f'Reading new data...')
        mw_on, mw_off = sweep(path)
        print(f'Data read out and saved to D:/QM_OPX/widefield_lib/{file_name}.npz')
print(f'Found data: D:/QM_OPX/widefield_lib/{file_name}.npz')
mw_on = np.load(f'D:/QM_OPX/widefield_lib/{file_name}.npz')['mw_on']
mw_off = np.load(f'D:/QM_OPX/widefield_lib/{file_name}.npz')['mw_off']
fig, (ax, ax2) = plt.subplots(2, 1)
divider = make_axes_locatable(ax2)
cax = divider.append_axes('right', size='5%', pad=0.05)
bin_width = 1
mw = mw_on / mw_off  # 1 - mw_on/mw_off
y = np.array([x.reshape(roi_size // bin_width, bin_width, roi_size // bin_width, bin_width).sum(3).sum(1) for x in
              mw]) / bin_width ** 2

x_idx = [int(x) for x in np.array(
    [50 / 60 * 1024, 515, np.random.randint(1024), np.random.randint(1024), np.random.randint(1024),
     np.random.randint(1024)]) / 1024 * y[0].shape[0]]
y_idx = [int(x) for x in np.array(
    [10 / 60 * 1024, 327, np.random.randint(1024), np.random.randint(1024), np.random.randint(1024),
     np.random.randint(1024)]) / 1024 * y[0].shape[1]]
for x_i, y_i in zip(x_idx, y_idx):
    odmr = np.array([k[x_i, y_i] for k in y])
    ax.plot(f_vec_array, odmr, zorder=1)
    ax2.plot(x_i, y_i, 'o', zorder=2)
    ax.set_xlabel('Frequency [GHz]')

while 1:
    for idx in range(0, n_f):
        im = ax2.imshow((1 - y[idx]) * 100, zorder=1, vmin=0, vmax=5)
        fig.colorbar(im, cax=cax, orientation='vertical')
        li = ax.axvline(f_vec_array[idx], label=f'{idx}', zorder=2)
        plt.pause(0.5)
        im.remove()
        li.remove()
plt.show()
