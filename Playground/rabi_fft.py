"""
A script to compute the Fast Fourier Transform of a Rabi Measurement. The Amplitude has not been reconstructed, but the
frequency is correct according to a sine wave put into the algorithm.
"""
import numpy as np
import matplotlib.pyplot as plt
from lib.data_handler import *
import scipy.fftpack

font = {#'family': 'normal',
    # 'weight' : 'bold',
    'size': 35}
matplotlib.rc('font', **font)
path = path_grabber("20221212", file_id=24)
entries = file_grabber(path)
file = [x for entry in entries for x in entry]

fig, ax = plt.subplots(1,1)#plot_ramsey(file['times'], file['counts'], file['counts2'])
for i in np.arange(0, len(file), 10):
    data = file[i][0]
    x = data['times'] * 4 * 1e-9
    y = data['counts']#-np.mean(data['counts'])
    y2 = data['counts']-np.mean(data['counts'][len(data['counts'])//6:])
    hann = np.hanning(len(x))
    hamm = np.hamming(len(x))
    f = np.fft.fft(hann * y, n=10000000)
    f2 = np.fft.fft(hann * y2, n=10000000)
    fa = 1 / (x[1] - x[0])
    N = len(f) // 2
    X = np.linspace(0, fa / 2, N, endpoint=True)
    #ax.plot(X, 2 / N * np.abs(f[:N]), linewidth=4, label='0')
    ax.plot(X, 2 / N * np.abs(f2[:N]), linewidth=4, label=f'ID={i};mean offset')
ax.set_xlabel('Frequency f [Hz]')
ax.set_ylabel('Amplitude')
ax.legend()
ax.grid()
for side in ax.spines.keys():
    ax.spines[side].set_linewidth(3)
ax.tick_params(axis='x', direction='in', length=8, width=3)
ax.tick_params(axis='y', direction='in', length=8, width=3)
ax.set_title('FFT of Signal')
plt.minorticks_on()
ax.xaxis.set_minor_locator(AutoMinorLocator(2))
ax.yaxis.set_minor_locator(AutoMinorLocator(2))
plt.grid(which='major', linewidth=1)
plt.grid(which='minor', linewidth=1, linestyle='--')
#plt.tight_layout()

plt.show()
# f = scipy.fftpack.fft(y)
#
# fr = (x[1]-x[0])*4 * np.linspace(0, 1, len(x)//2)
# y_m = 2/len(x) * abs(f[0:np.size(fr)])
# plt.plot(fr, y_m/max(y_m))
# plt.show()
