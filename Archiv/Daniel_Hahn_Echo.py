from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
# import matplotlib
# matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from configuration import *
from qm import SimulationConfig

################################
# Open quantum machine manager #
################################

qmm = QuantumMachinesManager()

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
t_max = 5000  # in clock cycles units
dt = 200  # in clock cycles units
t_vec = np.arange(t_min, t_max + dt/2, dt)  # +dt/2 to include t_max in array
n_avg = 1e6


with program() as hahn_echo:

    # Declare QUA variables
    ###################
    counts1 = declare(int)  # saves number of photon counts
    counts2 = declare(int)  # saves number of photon counts
    timestamps1 = declare(int, size=100)
    timestamps2 = declare(int, size=100)
    counts_1_st = declare_stream()  # stream for counts
    counts_2_st = declare_stream()  # stream for counts
    t = declare(int)  # variable to sweep over in time
    n = declare(int)  # variable to for_loop
    n_st = declare_stream()  # stream to save iterations

    # Pulse sequence
    ################
    play('laser_ON', 'AOM')  # Photoluminescence
    wait(100)
    with for_(n, 0, n < n_avg, n + 1):

        with for_(t, t_min, t <= t_max, t + dt):

            play('pi_half', 'NV')  # Pi/2 pulse to qubit
            wait(t, 'NV')  # variable delay in spin Echo
            play('pi', 'NV')  # Pi pulse to qubit
            wait(t, 'NV')  # variable delay in spin Echo
            play('pi_half', 'NV')  # Pi/2 pulse to qubit

            align()

            play('laser_ON', 'AOM')  # Photoluminescence
            measure('readout', 'APD', None,
                    time_tagging.analog(timestamps1, meas_len, counts1))
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

            play('laser_ON', 'AOM')  # Photoluminescence
            measure('readout', 'APD', None,
                    time_tagging.analog(timestamps2, meas_len, counts2))
            save(counts2, counts_2_st)  # save counts
            wait(100)


        save(n, n_st)  # save number of iteration inside for_loop

    # Stream processing
    ###################
    with stream_processing():
        counts_1_st.buffer(len(t_vec)).average().save('counts1')
        counts_2_st.buffer(len(t_vec)).average().save('counts2')
        n_st.save('iteration')

#######################
# Simulate or execute #
#######################

simulate = True

if simulate:
    qmm.simulate(config, hahn_echo, SimulationConfig(10000)).get_simulated_samples().con1.plot()
else:
    job = qm.execute(hahn_echo)  # execute QUA program

    res_handle = job.result_handles  # get access to handles
    vec_handle1 = res_handle.get('counts1')
    vec_handle2 = res_handle.get('counts2')
    vec_handle1.wait_for_values(1)
    iteration_handle = res_handle.get('iteration')
    iteration_handle.wait_for_values(1)

    while vec_handle1.is_processing():
        try:
            counts1 = vec_handle1.fetch_all()
            counts2 = vec_handle2.fetch_all()
            iteration = iteration_handle.fetch_all() + 1

        except Exception as e:
            pass

        else:
            plt.plot(4 * t_vec, counts1, counts2)
            plt.xlabel('t [ns]')
            plt.ylabel('Intensity [a.u.]')
            plt.title('Time Rabi')
            plt.pause(0.1)
            plt.clf()

    #counts1 = vec_handle1.fetch_all()
    #counts2 = vec_handle1.fetch_all()
    plt.plot(4 * t_vec, counts1, counts2)
    plt.xlabel('t [ns]')
    plt.ylabel('Intensity [a.u.]')
    plt.title('Time Rabi')
    plt.savefig('time_rabi.png')


