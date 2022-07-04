import matplotlib.pyplot as plt
from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *

from configuration import *

################################
# Open quantum machine manager #
################################

qmm = QuantumMachinesManager(host="192.168.1.254", port='80')
#
# ########################
# # Open quantum machine #
# ########################
#
qm = qmm.open_qm(config)
#
###################
# the qua program #
###################

# declare python variables
###########################
total_time = 100e4  # in ns
n_count = int(total_time / long_meas_len)

with program() as counter:

    # declare qua variables
    ###################
    signal = declare(int)  # saves number of photon counts
    total_signal = declare(int)
    timestamps = declare(int, size = 100)
    signal_st = declare_stream()
    n = declare(int)
    m = declare(int)
    state_0 = declare(bool)

    # pulse sequence
    ################
    with infinite_loop_():

        assign(total_signal, 0)  # set total_counts to zero

        with for_(n, 0, n < n_count, n + 1):
            #play('laser_ON', 'AOM', duration=long_meas_len // 4)  # photoluminescence
            #play('const', 'NV', duration=long_meas_len // 4)
            # measure('readout_cw', 'APD', None,
            #         integration.full('const', signal, "out1"))  # intensity on the photodiode, signal is fixed
            measure('readout_cw', 'APD', None,
                    time_tagging.analog(timestamps, long_meas_len, signal))
            assign(total_signal, total_signal + signal)

        save(total_signal, signal_st)  # save counts to stream variable


    # stream processing
    ###################
    with stream_processing():
        signal_st.with_timestamps().save('signal')

#######################
# simulate or execute #
#######################

job = qm.execute(counter)
res_handle = job.result_handles
vec_handle = res_handle.get('signal')
vec_handle.wait_for_values(1)
time = []
signal = []
while vec_handle.is_processing():
    try:
        new_signal = vec_handle.fetch_all()
    except Exception as e:
        print(e)
    else:
        signal.append(new_signal['value'])
        time.append(new_signal['timestamp'] * 1e-9)
        with open('../lib/logfile.txt', 'a') as file:
            file.write(f'{time[-1]},{signal[-1]}\n')
        if len(time) > 50:
            plt.plot(time[-50:], signal[-50:])
        else:
            plt.plot(time, signal)

        plt.xlabel('time [s]')
        plt.ylabel('intensity [a.u.]')
        plt.title('counter')
        plt.pause(0.1)
        plt.clf()
