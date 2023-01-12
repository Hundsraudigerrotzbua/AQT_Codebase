import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
work_dir = 'D:\\Widefield\\Daten\\telescope_max_focus\\'
roi_size = 1024
chunk_size = roi_size ** 2
file_name = 'mw_on'
path = work_dir + file_name + '.raw'
data = np.fromfile(path, dtype='uint16', sep="")
MW_on = data.reshape(500, 1024, 1024).astype(int)
#data = np.fromfile(path, dtype='uint16', sep="")
#MW_on = data[0:300*chunk_size].reshape(300, 1024, 1024).astype(int)
MW_on_sum = np.sum(MW_on, axis=0)
#MW_off = data[300*chunk_size:600*chunk_size].reshape(300, 1024, 1024).astype(int)
#MW_off_sum = np.sum(MW_off, axis=0)

file_name = 'mw_off'
path = work_dir + file_name + '.raw'
data = np.fromfile(path, dtype='uint16', sep="")
MW_off = data.reshape(500, 1024, 1024).astype(int)
MW_off_sum = np.sum(MW_off, axis=0)

plt.figure()
plt.imshow(MW_on_sum/MW_off_sum)
plt.colorbar()

#file_name = 'one_window_off'
#path = work_dir + file_name + '.raw'
#data = np.fromfile(path, dtype='uint16', sep="")
#MW_on = data[0:300*chunk_size].reshape(300, 1024, 1024).astype(int)
#MW_on_sum = np.sum(MW_on, axis=0)
#MW_off = data[300*chunk_size:600*chunk_size].reshape(300, 1024, 1024).astype(int)
#MW_off_sum = np.sum(MW_off, axis=0)
#
#
#plt.figure()
#plt.imshow(MW_off_sum-MW_on_sum)
#plt.colorbar()
