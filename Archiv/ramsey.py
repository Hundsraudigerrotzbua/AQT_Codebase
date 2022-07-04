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

t_min = 4  # in clock cycles units
t_max = 75 # in clock cycles units
dt = 2  # in clock cycles units
t_vec = np.arange(t_min, t_max + 0.1, dt)  # +dt/2 to include t_max in array
n_avg = 3e6
#measurement_length = 300


with program() as time_rabi:

    # Declare QUA variables
    ###################
    signal = declare(int)  # saves number of photon counts
    timestamps = declare(int, size = 100)
    signal_st = declare_stream()  # stream for counts
    t = declare(int)  # variable to sweep over in time
    a = declare(fixed)  # variable to sweep over the amplitude
    n = declare(int)  # variable to for_loop
    n_st = declare_stream()  # stream to save iterations

    # Pulse sequence
    ################
    play('laser_ON', 'AOM')  # Photoluminescence
    with for_(n, 0, n < n_avg, n + 1):

        with for_(t, t_min, t <= t_max, t + dt):
            play('pi', 'NV', duration=t)  # pulse of varied lengths
            align()
            wait(4)
            play('laser_ON', 'AOM')  # Photoluminescence
            measure('readout', 'APD', None,
                    time_tagging.analog(timestamps, meas_len, signal))
            save(signal, signal_st)  # save counts
            wait(100)
        save(n, n_st)  # save number of iteration inside for_loop

    # Stream processing
    ###################
    with stream_processing():
        signal_st.buffer(len(t_vec)).average().save('signal')
        n_st.save('iteration')

#######################
# Simulate or execute #
#######################

simulate = False

if simulate:
    qmm.simulate(config, time_rabi, SimulationConfig(10000)).get_simulated_samples().con1.plot()
else:
    job = qm.execute(time_rabi)  # execute QUA program

    res_handle = job.result_handles  # get access to handles
    vec_handle = res_handle.get('signal')
    vec_handle.wait_for_values(1)
    iteration_handle = res_handle.get('iteration')
    iteration_handle.wait_for_values(1)
    #signal = vec_handle.fetch_all()
    while vec_handle.is_processing():
        try:
            signal = vec_handle.fetch_all()
            iteration = iteration_handle.fetch_all() + 1

        except Exception as e:
            pass

        else:
            plt.plot(4 * t_vec, signal / (meas_len*1e-9))
            plt.xlabel('t [ns]')
            plt.ylabel('Intensity [a.u.]')
            plt.title('Time Rabi')
            plt.pause(0.1)
            plt.clf()

    signal = vec_handle.fetch_all() #Für Integration auskommentiert
    plt.plot(4 * t_vec, signal)
    plt.xlabel('t [ns]')
    plt.ylabel('Intensity [a.u.]')
    plt.title('Time Rabi')
    plt.savefig('time_rabi.png')
