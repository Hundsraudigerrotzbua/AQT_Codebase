from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from configuration import *
from qm import SimulationConfig

################################
# Open quantum machine manager #
################################

qmm = QuantumMachinesManager(host="192.168.1.254", port='80')

########################
# Open quantum machine #
########################

qm = qmm.open_qm(config)

###################
# The QUA program #
###################

# Declare Python variables
###########################

t_min = 1  # in clock cycles units
t_max = 75 # in clock cycles units
dt = 6  # in clock cycles units
t_vec = np.arange(t_min, t_max + dt/2, dt)  # +dt/2 to include t_max in array
n_avg = 0.5e6
#measurement_length = 300


with program() as time_rabi:

    # Declare QUA variables
    ###################
    signal = declare(int)  # saves number of photon counts
    timestamps = declare(int, size = int(meas_len / 500))
    signal_st = declare_stream()  # stream for counts
    t = declare(int)  # variable to sweep over in time
    a = declare(fixed)  # variable to sweep over the amplitude
    n = declare(int)  # variable to for_loop
    n_st = declare_stream()  # stream to save iterations

    # Finkler variables
    t_stop = 404
    t_len = 41
    t_vec = [int(t_) for t_ in np.linspace(4, t_stop, t_len)]
    rabi_vec = declare(int, size=t_len)
    t_ind = declare(int)
    m = declare(int)

    # Pulse sequence
    ################
    play('laser_ON', 'AOM')  # Photoluminescence
    with for_(n, 0, n < n_avg, n + 1):
        assign(t_ind, 0)
        with for_each_(t, t_vec):
            play('pi', 'NV', duration=t)  # pulse of varied lengths
            align()
            play('laser_ON', 'AOM')  # Photoluminescence
            measure('readout', 'APD', None,
                    time_tagging.analog(timestamps, meas_len, signal))
            with for_(m, 0, m < signal, m + 1):
                assign(rabi_vec[t_ind], rabi_vec[t_ind] + 1)
            assign(t_ind, t_ind + 1)


    with for_(t_ind, 0, t_ind < rabi_vec.length(), t_ind + 1):
        save(rabi_vec[t_ind], 'rabi')

#######################
# Simulate or execute #
#######################

simulate = False

if simulate:
    qmm.simulate(config, time_rabi, SimulationConfig(10000)).get_simulated_samples().con1.plot()
else:
    job = qm.execute(time_rabi)  # execute QUA program

    res_handle = job.result_handles  # get access to handles
    vec_handle = res_handle.get('rabi')
    vec_handle.wait_for_values(1)
    signal = vec_handle.fetch_all()['value']
    plt.figure()
    plt.plot(np.linspace(4, t_stop, t_len), signal)
    plt.xlabel('t [ns]')
    plt.ylabel('Intensity [a.u.]')
    plt.title('Time Rabi')
    plt.savefig('time_rabi.png')
