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

a_min = 0.1  # proportional factor to the pulse amplitude
a_max = 1  # proportional factor to the pulse amplitude
da = 0.05
a_vec = np.arange(a_min, a_max + 0.01, da)  # +da/2 to include a_max
n_avg = 1e6  # number of iterations

with program() as power_rabi:

    # Declare QUA variables
    ###################
    signal = declare(int)  # variable for number of counts
    signal_st = declare_stream()  # stream for counts
    timestamps = declare(int, size=100)
    a = declare(fixed)  # variable to sweep over the amplitude
    n = declare(int)  # variable to for_loop
    n_st = declare_stream()  # stream to save iterations

    # Pulse sequence
    ################
    play('laser_ON', 'AOM')  # Photoluminescence
    with for_(n, 0, n < n_avg, n + 1):

        with for_(a, a_min, a < a_max + da/2, a + da):
            play('pi'*amp(a), 'NV')  # pulse of varied amplitude
            align()
            play('laser_ON', 'AOM')  # Photoluminescence
            measure('readout', 'APD', None,
                    time_tagging.analog(timestamps, meas_len, signal))
            save(signal, signal_st)  # save counts

        save(n, n_st)  # save number of iteration inside for_loop

    # Stream processing
    ###################
    with stream_processing():
        signal_st.buffer(len(a_vec)).average().save('signal')
        n_st.save('iteration')

#######################
# Simulate or execute #
#######################

simulate = False

if simulate:
    qmm.simulate(config, power_rabi, SimulationConfig(10000)).get_simulated_samples().con1.plot()
else:
    job = qm.execute(power_rabi)  # execute QUA program

    res_handle = job.result_handles  # get access to handles
    vec_handle = res_handle.get('signal')
    vec_handle.wait_for_values(1)
    iteration_handle = res_handle.get('iteration')
    iteration_handle.wait_for_values(1)

    while vec_handle.is_processing():
        try:
            signal = vec_handle.fetch_all()
            iteration = iteration_handle.fetch_all() + 1

        except Exception as e:
            pass

        else:
            plt.plot(a_vec, signal )
            plt.xlabel('Amplitude')
            plt.ylabel('Intensity [a.u.]')
            plt.title('Power Rabi')
            plt.pause(0.1)
            plt.clf()

    signal = vec_handle.fetch_all()
    plt.plot(a_vec, signal )
    plt.xlabel('amplitude')
    plt.ylabel('Intensity [a.u.]')
    plt.title('Power Rabi')
