import matplotlib

matplotlib.use("TkAgg")
from lib.sequences import rabi

t_min = 16  # in clock cycles units
t_max = 200  # in clock cycles units
dt = 16  # in clock cycles units
n_avg = 3e6
t, s1, s2, iter = rabi(t_min, t_max, dt, n_avg=n_avg, ampli=2, plot=1)