from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
# from qm.simulate.credentials import create_credentials
import matplotlib.pyplot as plt
from configuration import *
from qm import SimulationConfig

################################
# Open quantum machine manager #
################################

#qmm = QuantumMachinesManager()
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

f_min = 2.8e9
f_max = 3e9

f_IF_min = f_min - NV_LO_freq #10e6  # begin freq sweep
f_IF_max = f_max - NV_LO_freq #250e6  # end of freq sweep
df = 5e6  # freq step
f_vec = np.arange(f_IF_min, f_IF_max + 0.1, df)  # f_max + df/2 so that f_max is included
#f_vec = np.flip(f_vec)
n_avg = 2e6  # number of averages

with program() as cw_odmr:

    # Declare QUA variables
    ###################
    signal = declare(int)  # variable for number of counts
    signal_st = declare_stream()  # stream for counts
    timestamps = declare(int, size = 100)
    f = declare(int)  # frequencies
    n = declare(int)  # number of iterations
    n_st = declare_stream()  # stream for number of iterations

    # Pulse sequence
    ################
    with for_(n, 0, n < n_avg, n + 1):

        with for_(f, f_IF_min, f <= f_IF_max, f + df):
        #with for_(f, f_IF_max, f >= f_IF_min, f - df):

            update_frequency('NV', f)  # updated frequency
            align()  # align all elements

            play('const', 'NV', duration=int(long_meas_len//4))  # play microwave pulse
            play('laser_ON', 'AOM', duration=int(long_meas_len//4))  # Photoluminescence
            measure('readout_cw', 'APD', None,
                    time_tagging.analog(timestamps, long_meas_len, signal))
            # measure('readout_cw', 'photo_diode', None,
            #         integration.full('const', signal, "out1"))  # intensity on the photodiode

            save(signal, signal_st)  # save counts on stream
            save(n, n_st)  # save number of iteration inside for_loop


    # Stream processing
    ###################
    with stream_processing():
        signal_st.buffer(len(f_vec)).average().save('signal')
        n_st.save('iteration')

#######################
# Simulate or execute #
#######################

simulate = False

if simulate:
    qmm.simulate(config, cw_odmr, SimulationConfig(int(1.1*meas_len))).get_simulated_samples().con1.plot()
    plt.show()
else:
    job = qm.execute(cw_odmr)  # execute QUA program

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
            plt.plot((NV_LO_freq + f_vec)*1e-9, signal)  # a.u.
            plt.plot([(NV_LO_freq + NV_IF_freq) * 1e-9, (NV_LO_freq + NV_IF_freq) * 1e-9],
                     [np.min(signal), np.max(signal)], '--',
                     color='k')
            plt.xlabel('f_vec [GHz]')
            plt.ylabel('Signal [kcps]')
            plt.title(f'ODMR at {mw_amp_NV} V_pp; {iteration} Iters')
            plt.pause(0.1)
            plt.clf()
            #print(iteration)

    signal = vec_handle.fetch_all()
    plt.plot((NV_LO_freq + f_vec)*1e-9, signal)  # a.u.
    plt.plot([(NV_LO_freq + NV_IF_freq) * 1e-9, (NV_LO_freq + NV_IF_freq) * 1e-9], [np.min(signal), np.max(signal)],
             '--', color='k')
    plt.xlabel('f_vec [GHz]')
    plt.ylabel('Signal [kcps]')
    plt.title(f'ODMR at {mw_amp_NV} V_pp; {iteration} Iters')
