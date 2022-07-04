from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from configuration import *
from qm import SimulationConfig
from sequences import hahn_echo

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
t_max = 125 # in clock cycles units
dt = 15 # in clock cycles units
t_vec = np.arange(t_min, t_max + 0.1, dt)  # +dt/2 to include t_max in array
n_avg = 10e6


with program() as time_rabi:

    # Declare QUA variables
    ###################
    counts1 = declare(int)  # saves number of photon counts
    counts2 = declare(int)  # saves number of photon counts
    counts_1_st = declare_stream()  # stream for counts
    counts_2_st = declare_stream()  # stream for counts
    timestamps_1 = declare(int, size = 100)
    timestamps_2 = declare(int, size = 100)
    t = declare(int)  # variable to sweep over in time
    a = declare(fixed)  # variable to sweep over the amplitude
    n = declare(int)  # variable to for_loop
    n_st = declare_stream()  # stream to save iterations

    # Pulse sequence
    ################
    play('laser_ON', 'AOM')  # Photoluminescence
    wait(100)
    with for_(n, 0, n < n_avg, n + 1):
        with for_(t, t_min, t <= t_max, t + dt):
            play('pi_half', 'NV')  # pulse of varied lengths
            wait(t/2, 'NV')
            #frame_rotation_2pi(1/2, 'NV')
            play('pi', 'NV')  # pulse of varied lengths
            wait(t/2, 'NV')
            play('pi_half', 'NV')  # pulse of varied lengths
            align()
            wait(4)

            play('laser_ON', 'AOM')
            measure('readout', 'APD', None,
                    time_tagging.analog(timestamps_1, meas_len, counts1))
            save(counts1, counts_1_st)  # save counts
            wait(100)

            align()

            play('pi_half', 'NV')  # Pi/2 pulse to qubit
            wait(t, 'NV')  # variable delay in spin Echo
            play('pi', 'NV')  # Pi pulse to qubit
            wait(t, 'NV')  # variable delay in spin Echo
            frame_rotation_2pi(0.5, 'NV')
            play('pi_half', 'NV')  # Pi/2 pulse to qubit
            reset_frame('NV')
            align()

            play('laser_ON', 'AOM')
            measure('readout', 'APD', None,
                    time_tagging.analog(timestamps_2, meas_len, counts2))
            save(counts2, counts_2_st)  # save counts
            wait(100)
        save(n, n_st)  # save number of iteration inside for_loop

    # Stream processing
    ###################
    with stream_processing():
        counts_1_st.buffer(len(t_vec)).average().save('signal1')
        counts_2_st.buffer(len(t_vec)).average().save('signal2')
        n_st.save('iteration')
#
#######################
# Simulate or execute #
#######################

simulate = False

if simulate:
    qmm.simulate(config, time_rabi, SimulationConfig(10000)).get_simulated_samples().con1.plot()
else:
    job = qm.execute(time_rabi)  # execute QUA program

    res_handle = job.result_handles  # get access to handles
    #vec_handle = res_handle.get('signal')
    vec_handle1 = res_handle.get('signal1')
    vec_handle2 = res_handle.get('signal2')
    vec_handle1.wait_for_values(1)
    iteration_handle = res_handle.get('iteration')
    iteration_handle.wait_for_values(1)
    signal = 0
    while vec_handle1.is_processing():
        try:
            signal1 = vec_handle1.fetch_all()
            signal2 = vec_handle2.fetch_all()
            iteration = iteration_handle.fetch_all() + 1

        except Exception as e:
            pass

        else:
            plt.plot(4 * t_vec, np.abs(signal1-signal2))# / (meas_len*1e-9))
            plt.xlabel('t [ns]')
            plt.ylabel('Normalized Signal')
            plt.title(f'Hahn Echo - {pi_amp_NV} Vpp; {iteration} Iters')
            plt.pause(0.1)
            plt.clf()

    #signal = vec_handle.fetch_all() #Für Integration auskommentiert
    signal1 = vec_handle1.fetch_all()
    signal2 = vec_handle2.fetch_all()
    #plt.plot(4 * t_vec, signal1/signal2)
    plt.plot(4 * t_vec, np.abs(signal1-signal2))
    plt.xlabel('t [ns]')
    plt.ylabel('Normalized Signal')
    plt.title(f'Hahn Echo - {pi_amp_NV} Vpp; {iteration} Iters')
    #plt.savefig('time_rabi.png')
