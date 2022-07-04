import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from lib.sequences import hahn_echo
import numpy as np
from lib.data_handler import Measurement

t_min = 8  # in clock cycles units
t_max = 1300  # in clock cycles units
dt = 80  # in clock cycles units
n_avg = 10.0e6


m = Measurement('Mikrowelle_an')
m.add_measurement('hahn_echo', t_min, t_max, dt, n_avg=n_avg, ampli=0, pulse_time=int(80), plot=1, fit=False)


#t_arr = []
#sig1_arr = []
#sig2_arr = []
#it_arr = []
#
#t, s1, s2, it = hahn_echo(t_min, t_max, dt, n_avg=n_avg, ampli=2, pulse_time=80, plot=1)
#t_arr.append(t)
#sig1_arr.append(s1)
#sig2_arr.append(s2)
#it_arr.append(it)
#np.savez('t_arr.npz', t_arr)
#np.savez('sig1_arr.npz', sig1_arr)
#np.savez('sig2_arr.npz', sig2_arr)
#np.savez('it_arr.npz', it_arr)
##plt.show()