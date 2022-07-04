import math

import matplotlib.pyplot as plt
from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
import matplotlib
matplotlib.use("TkAgg")
from qm import SimulationConfig
from qm import LoopbackInterface
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

def normaliization(counts_1_st, counts_2_st):
    counts_1 = declare(int)
    counts_2 = declare(int)
    timestamps1 = declare(int, size =100)
    timestamps2 = declare(int, size=100)
    play('laser_ON', 'AOM')
    measure('readout', 'APD', None,
            time_tagging.analog(timestamps1, meas_len, counts_1))
    wait(150 , 'APD2')
    measure('readout', 'APD2', None,
            time_tagging.analog(timestamps2, meas_len, counts_2))
    save(counts_1, counts_1_st)
    save(counts_2, counts_2_st)

# declare python variables
###########################
total_time = 100e4  # in ns
n_count = int(total_time / long_meas_len)

with program() as counter:

    # declare qua variables
    ###################
    counts_1_st = declare_stream()
    counts_2_st = declare_stream()
    n_st = declare_stream()
    n = declare(int, value = 0)
    m = declare(int)
    state_0 = declare(bool)

    # pulse sequence
    ################
    with infinite_loop_():
        wait(500)
        play('const','NV', duration= 260)
        normaliization(counts_1_st,counts_2_st)
        assign(n,n+1)
        save(n,n_st)



    # stream processing
    ###################
    with stream_processing():
        counts_1_st.average().save('signal1')
        counts_2_st.average().save('signal2')
        n_st.with_timestamps().save('n')


#######################
# simulate or execute #
#######################
simulate = False

if simulate:
    # simulation properties
    simulate_config = SimulationConfig(duration=int(1e4))
    job = qmm.simulate(config, counter, simulate_config)  # do simulation with qmm
    job.get_simulated_samples().con1.plot()  # visualize played pulses

else:
    job = qm.execute(counter)
    res_handle = job.result_handles
    vec_handle1 = res_handle.get('signal1')
    vec_handle2 = res_handle.get('signal2')
    vec_handle3 = res_handle.get('n')
    vec_handle1.wait_for_values(1)
    time = []
    signal1 = []
    signal2 = []
    while vec_handle1.is_processing():
        try:
            new_signal1 = vec_handle1.fetch_all()
            new_signal2 = vec_handle2.fetch_all()
            timestamps = vec_handle3.fetch_all()
        except exception as e:
            print(e)
        else:
            signal1.append(new_signal1/new_signal2 )
            #signal2.append(new_signal2)
            time.append(timestamps['timestamp'] * 1e-9)
            if len(time) > 50:
                plt.plot(time[-50:], signal1[-50:])
                #plt.plot(time[-50:], signal2[-50:])
            else:
                plt.plot(time, signal1)
                #plt.plot(time, signal2)

            plt.xlabel('time [s]')
            plt.ylabel('intensity [a.u.]')
            plt.title('counter')
            plt.pause(0.1)
            plt.clf()
