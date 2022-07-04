from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
import matplotlib.pyplot as plt
from configuration import *

qmm = QuantumMachinesManager(host="192.168.1.254", port='80')
qm = qmm.open_qm(config)

total_time = 0.1  # 100ms
cw_time_sec = 50e-6  # 50us
cw_time_cycles = int(cw_time_sec * 1e9 // 4)
n_count = int(total_time / cw_time_sec)

with program() as counter:
    times = declare(int, size=1000)
    counts = declare(int)
    total_counts = declare(int)
    counts_st = declare_stream()
    n = declare(int)
    with infinite_loop_():
        with for_(n, 0, n < n_count, n + 1):
            play('laser_ON', 'AOM', duration=cw_time_cycles)
            #play('const', 'NV', duration=int(long_meas_len // 4))  # play microwave pulse
            measure('readout', 'APD', None, time_tagging.analog(times, 4 * cw_time_cycles, counts))
            assign(total_counts, total_counts + counts)
        save(total_counts, counts_st)
        assign(total_counts, 0)

    with stream_processing():
        counts_st.with_timestamps().save('counts')

job = qm.execute(counter)
res_handle = job.result_handles
vec_handle = res_handle.get('counts')
vec_handle.wait_for_values(1)
time = []
counts = []
a = np.zeros(50)
# a = []
while vec_handle.is_processing():
    try:
        new_counts = vec_handle.fetch_all()

    except Exception as e:
        print(e)
    else:
        # a.append(new_counts['value'] / total_time)
        a = np.roll(a, -1)
        a[-1] = new_counts['value'] / total_time
        b = np.round(np.mean(a), 3)
        c = np.round(np.std(a), 3)
        counts.append(new_counts['value'] / total_time)
        time.append(new_counts['timestamp'] * 1e-9)

        if len(time) > 50:
            plt.plot(time[-50:], counts[-50:], label=f'mean={b}, std={c}')
        else:
            plt.plot(time, counts, label=f'mean={b}, std={c}')
        plt.legend()
        plt.xlabel('time [s]')
        plt.ylabel('counts [kcps]')
        plt.title(f'Counter')
        plt.pause(0.1)
        plt.clf()
