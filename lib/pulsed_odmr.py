from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
# from qm.simulate.credentials import create_credentials
import matplotlib.pyplot as plt
from configuration import *

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

tau_min = 16 // 4 # ns to cycles
tau_max = 150 // 4
dtau = 10 // 4
ntau = 10 # ten sweeps, since matplotlib colorwheel has 10 unique entries

f_min = 2.8e9
f_max = 3e9
f_IF_min = f_min - NV_LO_freq #10e6  # begin freq sweep
f_IF_max = f_max - NV_LO_freq #250e6  # end of freq sweep
df = 5e6  # freq step
f_vec = np.arange(f_IF_min, f_IF_max + 0.1, df)  # f_max + df/2 so that f_max is included
#f_vec = np.flip(f_vec)
n_avg = 2e6  # number of averages
ampli = 1

save_dir = 'C:\\Data\\OPX_Datadump\\20220425'

for tau in np.linspace(tau_min, tau_max+0.1, ntau):
#for tau in np.arange(tau_min, tau_max+0.1, dtau):
    with program() as cw_odmr:
        # Declare QUA variables
        ###################
        signal = declare(int)  # variable for number of counts
        signal_st = declare_stream()  # stream for counts
        timestamps = declare(int, size=100)
        f = declare(int)  # frequencies
        t = declare(int)  # variable to sweep over in time
        t = tau
        a = declare(fixed)  # variable to sweep over the amplitude
        a = ampli
        n = declare(int)  # number of iterations
        n_st = declare_stream()  # stream for number of iterations

        # Pulse sequence
        ################
        play('laser_ON', 'AOM')  # Photoluminescence
        with for_(n, 0, n < n_avg, n + 1):
            with for_(f, f_IF_min, f <= f_IF_max, f + df):
                update_frequency('NV', f)  # updated frequency
                align()  # align all elements
                play('pi' * amp(a), 'NV', duration=t)  # pulse of varied lengths
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
            signal_st.buffer(len(f_vec)).average().save('signal')
            n_st.save('iteration')

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
            plt.plot(NV_LO_freq + f_vec, signal)  # a.u.
            plt.plot([NV_LO_freq + NV_IF_freq, NV_LO_freq + NV_IF_freq], [np.min(signal), np.max(signal)], '--',
                     color='k')
            plt.xlabel('f_vec [Hz]')
            plt.ylabel('intensity [a.u.]')
            plt.title(f'Pulsed ODMR - tau={4*tau}ns at {pi_amp_NV*ampli} V')
            plt.pause(0.1)
            plt.clf()
            #print(iteration)

    signal = vec_handle.fetch_all()
    plt.plot(NV_LO_freq + f_vec, signal)  # a.u.
    plt.plot([NV_LO_freq + NV_IF_freq, NV_LO_freq + NV_IF_freq], [np.min(signal), np.max(signal)], '--', color='k')
    plt.xlabel('f_vec [Hz]')
    plt.ylabel('intensity [a.u.]')
    plt.title(f'Pulsed ODMR - tau={4 * tau}ns at {pi_amp_NV * ampli} V')
    print(f'Saving... {tau*4}')
    np.savez(save_dir + f'\\pulsed_odmr_{str(int(tau*4)).zfill(3)}ns', [f_vec, signal])
