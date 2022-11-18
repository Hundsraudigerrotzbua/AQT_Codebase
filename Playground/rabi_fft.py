import numpy as np
import matplotlib.pyplot as plt
import scipy.fftpack

path = 'D:\\QM_OPX\\Data\\2022\\11\\20221116\\rabi\9_20221116-134720_Rabi_Time-Power_Graph\\1_3_221116-144202_Rabi_Time-Power_Graph_f2870000000.0_a0.0353623046875.npz'

data = np.load(path)

x = data['times'] * 4 * 1e-9
y = data['counts']
hann = np.hanning(len(x))
hamm = np.hamming(len(x))
f = np.fft.fft(hann * y, n=10000000)
fa = 1 / (x[1] - x[0])
N = len(f) // 2
X = np.linspace(0, fa / 2, N, endpoint=True)
plt.plot(X, 2 / N * np.abs(f[:N]))
plt.show()

# f = scipy.fftpack.fft(y)
#
# fr = (x[1]-x[0])*4 * np.linspace(0, 1, len(x)//2)
# y_m = 2/len(x) * abs(f[0:np.size(fr)])
# plt.plot(fr, y_m/max(y_m))
# plt.show()
