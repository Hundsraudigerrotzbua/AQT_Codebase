import matplotlib.pyplot as plt
from lib.data_handler import path_grabber, file_grabber
from lib.fit_lib import *

path = path_grabber('20221117', 'ramsey', 5)
meas_ID = 0
optim_ID = 11
data = file_grabber(path, meas_ID, optim_ID)[0][0]
print(data[1])
data = data[0]

t = np.array(data['times'].tolist()) * 4
y = np.array(data['counts'].tolist())
y = y / np.max(y)

yf = fit_ramsey(t, y, amp_g=y[0])


#def corr_func(x, a, b, c, d, e):
#    return np.exp(-a * x) * (b * np.sin(2 * np.pi * c * x + d)) + e
#
#
#dec_model = Model(corr_func, nan_policy='propagate')
#results = dec_model.fit(y, x=t, a=1e-9, b=y[0], c=1 / 500, d=0, e=np.mean(y))

fig, ax = plt.subplots()
ax.plot(t, y)
ax.plot(t, yf)
#ax.annotate(f'$t_{{\\pi}}$= {t_rabi} ns\n $t_{{\\frac{{\\pi}}{{2}}}}$= {t_rabi/2} ns', xy=(0.95, 0.85),
#            xycoords='axes fraction',
#            size=15, ha='right', va='bottom', bbox=dict(boxstyle='round', fc='w'))
#plt.legend()
plt.show()
