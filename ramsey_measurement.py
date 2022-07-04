import matplotlib

matplotlib.use("TkAgg")

from lib.sequences import ramsey

t_min = 16  # in clock cycles units
t_max = 240  # in clock cycles units
dt = 16  # in clock cycles units
n_avg = 12e6

ramsey(t_min, t_max, dt, n_avg=12e6, ampli=2, pulse_time=80, plot=1)
