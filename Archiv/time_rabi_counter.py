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

t_min = 10  # in clock cycles units
t_max = 125  # in clock cycles units
dt = 5  # in clock cycles units
t_vec = np.arange(t_min, t_max + dt/2, dt)  # +dt/2 to include t_max in array
n_avg = 1e6
total_time = 100e4  # in ns
n_count = int(total_time / long_meas_len)

with program() as time_rabi:

    # Declare QUA variables
    ###################
    signal = declare(int)  # saves number of photon counts
    total_signal = declare(int)  # saves number of photon counts
    counts = declare(int)  # saves number of photon counts
    timestamps = declare(int, size = 100)
    timestamps2 = declare(int, size=100)
    signal_st = declare_stream()  # stream for counts
    counts_st = declare_stream()  # stream for counts
    t = declare(int)  # variable to sweep over in time
    a = declare(fixed)  # variable to sweep over the amplitude
    n = declare(int)  # variable to for_loop
    m = declare(int)  # variable to for_loop
    n_st = declare_stream()  # stream to save iterations

    # Pulse sequence
    ################
    with infinite_loop_():
        assign(total_signal, 0)  # set total_counts to zero

        with for_(m, 0, m < n_count, m + 1):
            play('laser_ON', 'AOM')
            measure('readout_cw', 'APD2', None,
                    time_tagging.analog(timestamps2, 3000, signal))
            assign(total_signal, total_signal + signal)

        save(total_signal, signal_st)  # save counts to stream variable

    # play('laser_ON', 'AOM')  # Photoluminescence
    # with for_(n, 0, n < n_avg, n + 1):
    #
    #     with for_(t, t_min, t <= t_max, t + dt):
    #         play('pi', 'NV', duration=t)  # pulse of varied lengths
    #         align()
    #         play('laser_ON', 'AOM')  # Photoluminescence
    #         # measure('readout', 'APD', None,
    #         #         time_tagging.analog(timestamps, meas_len, counts))
    #         #save(counts, counts_st)  # save counts
    #         wait(1000)

        #save(n, n_st)  # save number of iteration inside for_loop


    # Stream processing
    ###################
    with stream_processing():
        #counts_st.buffer(len(t_vec)).average().save('counts')
        signal_st.with_timestamps().save('signal')
        #n_st.save('iteration')

#######################
# Simulate or execute #
#######################

simulate = False

if simulate:
    qmm.simulate(config, time_rabi, SimulationConfig(10000)).get_simulated_samples().con1.plot()
else:
    job = qm.execute(time_rabi)  # execute QUA program
    res_handle = job.result_handles
    vec_handle = res_handle.get('signal')
    vec_handle.wait_for_values(1)
    time = []
    signal = []
    while vec_handle.is_processing():
        try:
            new_signal = vec_handle.fetch_all()
        except exception as e:
            print(e)
        else:
            signal.append(new_signal['value'])
            time.append(new_signal['timestamp'] * 1e-9)
            if len(time) > 50:
                plt.plot(time[-50:], signal[-50:])
            else:
                plt.plot(time, signal)

            plt.xlabel('time [s]')
            plt.ylabel('intensity [a.u.]')
            plt.title('counter')
            plt.pause(0.1)
            plt.clf()
    # job = qm.execute(time_rabi)  # execute QUA program
    #
    # res_handle = job.result_handles  # get access to handles
    # vec_handle = res_handle.get('signal')
    # vec_handle.wait_for_values(1)
    # iteration_handle = res_handle.get('iteration')
    # iteration_handle.wait_for_values(1)
    #
    # while vec_handle.is_processing():
    #     try:
    #         signal = vec_handle.fetch_all()
    #         iteration = iteration_handle.fetch_all() + 1
    #
    #     except Exception as e:
    #         pass
    #
    #     else:
    #         plt.plot(4 * t_vec, signal)
    #         plt.xlabel('t [ns]')
    #         plt.ylabel('Intensity [a.u.]')
    #         plt.title('Time Rabi')
    #         plt.pause(0.1)
    #         plt.clf()
    #
    # signal = vec_handle.fetch_all()
    # plt.plot(4 * t_vec, signal)
    # plt.xlabel('t [ns]')
    # plt.ylabel('Intensity [a.u.]')
    # plt.title('Time Rabi')
    # plt.savefig('time_rabi.png')
