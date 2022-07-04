from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
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
t_max = 50  # in clock cycles units
dt = 4  # in clock cycles units
t_vec = np.arange(t_min, t_max + dt/2, dt)  # +dt/2 to include t_max in array
n_avg = 3e6

def normalization(counts_1_st, counts_2_st):
    counts_1 = declare(int)
    counts_2 = declare(int)
    timestamps1 = declare(int, size =100)
    timestamps2 = declare(int, size=100)
    play('laser_ON', 'AOM')
    measure('readout', 'APD', None,
            time_tagging.analog(timestamps1, meas_len, counts_1))
    wait((laser_len-3*meas_len)//4 , 'APD2')
    measure('readout', 'APD2', None,
            time_tagging.analog(timestamps2, meas_len, counts_2))
    save(counts_1, counts_1_st)
    save(counts_2, counts_2_st)


ampli = 1
with program() as time_rabi:

    # Declare QUA variables
    ###################
    signal = declare(int)  # saves number of photon counts
    timestamps = declare(int, size = 100)
    signal_st = declare_stream()  # stream for counts
    counts_1_st = declare_stream()  # stream for counts
    counts_2_st = declare_stream()  # stream for counts
    t = declare(int)  # variable to sweep over in time
    b = 2
    a = declare(fixed, value=b)  # variable to sweep over the amplitude
    n = declare(int)  # variable to for_loop
    n_st = declare_stream()  # stream to save iterations

    # Pulse sequence
    ################
    play('laser_ON', 'AOM')  # Photoluminescence
    with for_(n, 0, n < n_avg, n + 1):

        with for_(t, t_min, t <= t_max, t + dt):
        #with for_(a, a_min, a < a_max + da / 2, a + da):
            play('pi'*amp(a), 'NV', duration=t)  # pulse of varied lengths
            #play('pi' * amp(a), 'NV')  # pulse of varied amplitude
            align()
            wait(4)
            normalization(counts_1_st, counts_2_st)
            # measure('readout', 'APD', None,
            #         time_tagging.analog(timestamps, meas_len, signal))
            #save(signal, signal_st)  # save counts
            wait(100)
        save(n, n_st)  # save number of iteration inside for_loop

    # Stream processing
    ###################
    with stream_processing():
        counts_1_st.buffer(len(t_vec)).average().save('signal1')
        counts_2_st.buffer(len(t_vec)).average().save('signal2')
        #signal_st.buffer(len(t_vec)).average().save('signal')
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
    #vec_handle = res_handle.get('signal')
    vec_handle1 = res_handle.get('signal1')
    vec_handle2 = res_handle.get('signal2')
    vec_handle1.wait_for_values(1)
    iteration_handle = res_handle.get('iteration')
    iteration_handle.wait_for_values(1)
    fig = plt.figure()
    ax = plt.gca()
    ax2 = ax.twinx()

    while vec_handle1.is_processing():
        try:
            #signal = vec_handle.fetch_all()
            signal1 = vec_handle1.fetch_all()
            signal2 = vec_handle2.fetch_all()
            iteration = iteration_handle.fetch_all() + 1

        except Exception as e:
            pass

        else:
            pl1 = ax.plot(4 * t_vec, signal1, color='blue', label='Signal1')
            pl2 = ax.plot(4 * t_vec, signal2, color='red', label='Signal2')
            pl3 = ax2.plot(4*t_vec, signal1-signal2, color='k', label='Signal1/Signal2')
            ax.set_xlabel('t [ns]')
            ax.set_ylabel('Signal 1 and 2')
            ax2.set_ylabel('Signal1/Signal2')
            plt.title(f'Time Rabi normalized at {pi_amp_NV*ampli} V; {iteration} Iters')
            ln = pl1 + pl2 + pl3
            labs = [l.get_label() for l in ln]
            plt.legend(ln, labs, loc=0)
            plt.pause(0.1)
            ax.clear()
            ax2.clear()


    #signal1 = vec_handle1.fetch_all()
    #signal2 = vec_handle1.fetch_all()
    pl1 = ax.plot(4 * t_vec, signal1, color='blue', label='Signal1')
    pl2 = ax.plot(4 * t_vec, signal2, color='red', label='Signal2')
    pl3 = ax2.plot(4 * t_vec, signal1 - signal2, color='k', label='Signal1/Signal2')
    ln = pl1 + pl2 + pl3
    labs = [l.get_label() for l in ln]
    plt.legend(ln, labs, loc=0)
    ax.set_xlabel('t [ns]')
    ax.set_ylabel('Signal 1 and 2')
    ax2.set_ylabel('Signal1/Signal2')
    plt.title(f'Time Rabi normalized at {pi_amp_NV*ampli} V; {iteration} Iters')
    plt.legend()
    #plt.savefig('time_rabi.png')
