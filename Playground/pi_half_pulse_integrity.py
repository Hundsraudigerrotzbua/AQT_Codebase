"""
The counts for the ramsey measurement with a frame rotation look strange, in a way that both traces (with x and -x pulse)
appear to be at the same mixed state after the pi half pulses. For longer wait times the separation increases.
This script is to check the integrity of pi half pulses by simply doing a pi half pulse, noting the counts for a
fixed waiting time and repeating this. Results are plotted over the number of averages.
"""

from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
from qm import SimulationConfig
from configuration import *
from qualang_tools.plot import interrupt_on_close
from qualang_tools.results import progress_counter, fetching_tool
from lib.qudi_communication import run_kernel_command
from lib.data_handler import *
from lib.sequences import setup_qm

n_avg = 10e6
pi_half_time = 313
wait_time = 16 // 4
with program() as time_rabi:
    n = declare(int)
    counts = declare(int)
    counts_sum = declare(int)
    counts2 = declare(int)
    counts_sum2 = declare(int)
    c = declare(int)
    times = declare(int, size=100)
    times2 = declare(int, size=100)
    counts_st = declare_stream()
    counts_st2 = declare_stream()
    n_st = declare_stream()

    play("laser_ON", "AOM")
    wait(100, "AOM")
    with for_(n, 0, n < n_avg, n + 1):
        play("const", "NV", duration=(3*pi_half_time) // 4)  # pulse of varied lengths
        #align()
        #wait(wait_time, 'NV')
        #play("const", "NV", duration=pi_half_time // 4)  # pulse of varied lengths
        align()
        play("laser_ON", "AOM")
        measure("readout", "APD", None, time_tagging.analog(times, meas_len, counts))
        assign(counts_sum, counts_sum + counts)  # save counts
        wait(500)
#
#        align()
#
#        play("const", "NV", duration=pi_half_time // 4)  # pulse of varied lengths
#        wait(wait_time, "NV")  # variable delay in spin Echo
#        frame_rotation_2pi(0.5, "NV")  # Turns next pulse to -x
#        play("const", "NV", duration=pi_half_time // 4)  # pulse of varied lengths
#        reset_frame("NV")
#        align()
        align()
        wait((pi_half_time*2)//4 + wait_time)
        play("laser_ON", "AOM")
        measure("readout", "APD", None, time_tagging.analog(times2, meas_len, counts2))
        assign(counts_sum2, counts_sum2 + counts2)  # save counts
        save(counts_sum, counts_st)  # save number of iteration inside for_loop
        save(counts_sum2, counts_st2)  # save number of iteration inside for_loop
        save(n, n_st)  # save number of iteration inside for_loop
        wait(500)

    with stream_processing():
        counts_st.save("counts")
        counts_st2.save("counts2")
        n_st.save("iteration")

qmm, qm = setup_qm()
job = qm.execute(time_rabi)
res_handles = job.result_handles
times_handle = res_handles.get("counts")
times2_handle = res_handles.get("counts2")
times_handle.wait_for_values(1)
times2_handle.wait_for_values(1)
results = fetching_tool(job, data_list=["counts", "counts2", "iteration"], mode="live")
fig, ax = plt.subplots(1,1)
interrupt_on_close(fig, job)
n_vec = []
c_vec = []
c_vec2 = []
while results.is_processing():
    ax.clear()
    counts, counts2, iteration = results.fetch_all()
    n_vec.append(iteration)
    c_vec.append(counts/meas_len/iteration)
    c_vec2.append(counts2/meas_len/iteration)
    ax.plot(n_vec, np.array(c_vec))
    ax.plot(n_vec, np.array(c_vec2))
    plt.pause(0.1)

job.halt()

