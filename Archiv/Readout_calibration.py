from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
from qm import LoopbackInterface
# from qm.simulate.credentials import create_credentials
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
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

n_avg = 1e5  # number of averages

with program() as readout_calibration:

    # Declare QUA variables
    ###################
    n = declare(int)  # number of iterations
    n_st = declare_stream()  # stream for number of iterations
    timestamps_st = declare_stream()  # stream for number of iterations
    timestamps = declare(int, size=10)
    counts = declare(int)
    # Pulse sequence
    ################
    play('laser_ON', 'AOM', duration=int(meas_len // 4))  # Photoluminescence
    with for_(n, 0, n < n_avg, n + 1):
        wait(100)
        align()  # align all elements
        #play("const","NV")
        play('laser_ON', 'AOM', duration=int(meas_len//4))  # Photoluminescence
        measure('readout', 'APD', None, time_tagging.analog(timestamps, 1000, counts))  # intensity on the photodiode

        for i in range(10):
            save(timestamps[i], timestamps_st)

    # Stream processing
    ###################
    with stream_processing():
        timestamps_st.save_all('timestamps')


#######################
# Simulate or execute #
#######################

simulate = False

if simulate:
    job = qmm.simulate(config, readout_calibration, SimulationConfig(int(10.1*meas_len),simulation_interface=LoopbackInterface([("con1", 1, "con1", 1)], latency=184)))
    # job.get_simulated_samples().con1.plot()
    # plt.show()
    res = job.result_handles
    res.wait_for_all_values()
    raw_adc = res.raw_adc.fetch_all()['value']
    plt.plot(raw_adc)
else:
    job = qm.execute(readout_calibration)  # execute QUA program
    res_handle = job.result_handles
    res_handle.wait_for_all_values()
    gg = res_handle.timestamps.fetch_all().tolist()
    gg2 = [x[0] for x in gg]
    plt.hist(gg2, 1000)
    # res_handle = job.result_handles  # get access to handles
    # vec_handle = res_handle.raw_adc.fetch_all()['value']
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
    #         plt.plot(signal)  # a.u.
    #         plt.xlabel('time [ns]')
    #         plt.ylabel('intensity [a.u.]')
    #         plt.title('Raw_adc')
    #         plt.pause(0.1)
    #         plt.clf()
    #         print(iteration)
    #
    # signal = vec_handle.fetch_all()
    # plt.plot(NV_LO_freq + f_vec, signal)  # a.u.
    # plt.xlabel('f_vec [Hz]')
    # plt.ylabel('intensity [a.u.]')
    # plt.title('ODMR')
