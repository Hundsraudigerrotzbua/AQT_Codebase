from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
import numpy as np
import matplotlib.pyplot as plt
from configuration import *
from qm import SimulationConfig

qmm = QuantumMachinesManager(host="192.168.1.254", port='80')
qm = qmm.open_qm(config)

total_time = 0.1  # 100ms
cw_time_sec = 500e-6  # 50us
cw_time_cycles = int(cw_time_sec * 1e9 // 4)
n_count = int(total_time / cw_time_sec)

with program() as counter_all:
    times = declare(int, size=1000)
    counts = declare(int)
    total_counts = declare(int)
    counts_st = declare_stream()
    n = declare(int)
    with infinite_loop_():
        with for_(n, 0, n < n_count, n + 1):
            play('laser_ON', 'AOM', duration=cw_time_cycles)
            measure('readout', 'APD', None, time_tagging.analog(times, 4 * cw_time_cycles, counts))
            assign(total_counts, total_counts + counts)
        save(total_counts, counts_st)
        assign(total_counts, 0)

    with stream_processing():
        counts_st.with_timestamps().save_all('counts')

job = qm.execute(counter_all)
res_handle = job.result_handles
vec_handle = res_handle.get('counts')
vec_handle.wait_for_values(1)
time = []
counts = []
prev_index = 0
while res_handle.is_processing():
    try:
        new_index = vec_handle.count_so_far()
        if new_index > prev_index:
            new_counts = vec_handle.fetch(slice(prev_index, new_index))
            prev_index = new_index

            counts.append((new_counts['value'] / total_time / 1000).tolist())
            time.append((new_counts['timestamp'] * 1e-9).tolist())
            if len(time) > 50:
                plt.plot(time[-50:], counts[-50:])
            else:
                plt.plot(time, counts)

            plt.xlabel('time [s]')
            plt.ylabel('counts [kcps]')
            plt.title('Counter')
            plt.pause(0.1)
            plt.clf()

    except Exception as e:
        print(e)

