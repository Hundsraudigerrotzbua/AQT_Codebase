from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
# from qualang_tools.addons.InteractivePlotLib import InteractivePlotLib
import matplotlib
matplotlib.use("TkAgg")
from configuration import *
from qm import SimulationConfig
from qm import LoopbackInterface

################################
# Open quantum machine manager #
################################

# qmm = QuantumMachinesManager()
qmm = QuantumMachinesManager(host = "192.168.1.254", port = '80')

########################
# Open quantum machine #
########################

qm = qmm.open_qm(config)
'''
qm.set_dc_offset_by_qe('NV', 'I', 0.2)
qm.set_dc_offset_by_qe('NV', 'Q', 0.2)
'''
###################
# The QUA program #
###################

simulate = False

with program() as hello_qua:
    raw_adc = declare_stream(adc_trace=True)
    # wait(100,'NV')
    #update_frequency('NV', 0)
    #play('const', 'NV')
    #align('NV','APD')
    wait(100, 'AOM')
    play('laser_ON', 'AOM', duration=1000)
    measure('readout', 'APD', raw_adc)

    with stream_processing():
        raw_adc.input1().save('raw_adc')

with program() as hello_qua2:
    signal = declare(fixed)
    raw_adc = declare_stream(adc_trace=True)
    #update_frequency('NV', 50e6)
    with infinite_loop_():
        #play('laser_ON','AOM', duration = 200)
        play('const','NV', duration = 200)
        #wait(10000000)


n_avg = 1e4
with program() as hello_qua3:
    timestamps = declare(int, size=100)
    counts = declare(int)
    bins = [declare(int, value=0) for _ in range(30)]
    t = declare(int)
    n = declare(int)
    # wait(100,'NV')
    #update_frequency('NV', 0)
    #play('const', 'NV')
    #align('NV','APD')
    with for_(n, 0, n < n_avg, n + 1):
        play('laser_ON', 'AOM', duration=10)
        measure('readout_cw', 'APD', None,
                time_tagging.analog(timestamps, 600, counts))

        with for_(t, 0, t < timestamps.length(), t + 1):
            for i, bin in enumerate(bins):
                with if_((timestamps[t] < (i + 1) * 20) & (timestamps[t] > i * 20)):
                    assign(bin, bin + 1)

    for i, bin in enumerate(bins):
        save(bin, 'histo')

    #with stream_processing():
    #    raw_adc.input1().save('raw_adc')

#######################
# Simulate or execute #
#######################

if simulate:

    simulate_config = SimulationConfig(duration=int(1000), simulation_interface=LoopbackInterface(([('con1', 1, 'con1', 1)]))) # simulation properties
    job = qmm.simulate(config, hello_qua, simulate_config)  # do simulation
    #job.get_simulated_samples().con1.plot()  # visualize played pulses
    #res_handle = job.result_handles
    #vec_handle = res_handle.get('raw_adc').fetch_all()
    #plt.plot(vec_handle)


else:
    job = qm.execute(hello_qua2)
    # job.result_handles.wait_for_all_values()
    # res_handle = job.result_handles
    # #res_handle.histo.fetch_all()
    # vec_handle = res_handle.get('raw_adc').fetch_all()
    # plt.plot(vec_handle)
    # job = qm.execute(hello_qua2)
    # simulate_config = SimulationConfig(duration=int(1000))
    # job=qmm.simulate(config, hello_qua, simulate_config)
    # job.get_simulated_samples().con1.plot()  # visualize played pulses

