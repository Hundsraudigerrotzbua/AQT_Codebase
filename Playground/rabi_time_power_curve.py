import matplotlib.pyplot as plt
from lib.data_handler import path_grabber, file_grabber
from lib.fit_lib import *
from lib.misc_lib import *


path = path_grabber('20221116', 'rabi', 10)
optim_ID = 3
rabi_times = []
t_arr =  []
y_arr = []
yf_arr = []
amp_array = dbm_to_vp(np.linspace(-27, -6, 8))/0.07
amp_array = [x for x in amp_array if x < 2-2**-16] # the amp(x) value can't exceed 2-2**-16 (QM Documentation)

for meas_ID in range(0, 7):
    data = file_grabber(path, meas_ID, optim_ID)[0][0][0]
    t = np.array(data['times'].tolist()) * 4
    y = np.array(data['counts'].tolist())
    y = y / np.max(y)

    yf, t_rabi = fit_rabi(t, y, amp_g=y[0], off_g=np.mean(y))
    y_arr.append(y)
    yf_arr.append(yf)
    t_arr.append(t)
    rabi_times.append(t_rabi)

fig, (ax1, ax2) = plt.subplots(2, 1)
ax1.scatter(amp_array, 1/(2*np.pi*np.array(rabi_times)) * 1e6)
colors = ['b', 'g', 'brown', 'orange', 'black', 'grey', 'purple']
for time, data, fit, c, ra, pw in zip(t_arr, y_arr, yf_arr, colors, rabi_times, amp_array):
    ax2.plot(time, data, color=c, label=f't={ra}, pw={pw*0.07}')
    ax2.plot(time, fit, 'r')

plt.legend(prop={'size':9})
plt.show()
