"""
A Rabi experiment sweeping the duration of the MW pulse.
"""
from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
from qm import SimulationConfig
import matplotlib.pyplot as plt
from configuration import *
from qualang_tools.plot import interrupt_on_close
from qualang_tools.results import progress_counter, fetching_tool
from lib.qudi_communication import run_kernel_command

###################
# The QUA program #
###################

t_min = 16 // 4  # in clock cycles units (must be >= 4)
t_max = 3000 // 4  # in clock cycles units
dt = 100 // 4  # in clock cycles units
t_vec = np.arange(t_min, t_max + 0.1, dt)  # +0.1 to include t_max in array
n_avg = 10e6

with program() as time_rabi:
    counts = declare(int)  # variable for number of counts
    counts_st = declare_stream()  # stream for counts
    times = declare(int, size=100)
    t = declare(int)  # variable to sweep over in time
    n = declare(int)  # variable to for_loop
    n_st = declare_stream()  # stream to save iterations

    play("laser_ON", "AOM")
    wait(100, "AOM")
    with for_(n, 0, n < n_avg, n + 1):
        with for_(t, t_min, t <= t_max, t + dt):
            play("const", "NV", duration=t)  # pulse of varied lengths
            align()
            play("laser_ON", "AOM")
            measure("readout", "APD", None, time_tagging.analog(times, meas_len, counts))
            save(counts, counts_st)  # save counts
            wait(100)

        save(n, n_st)  # save number of iteration inside for_loop

    with stream_processing():
        counts_st.buffer(len(t_vec)).average().save("counts")
        n_st.save("iteration")

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
            # play('const', 'NV', duration=int(long_meas_len // 4))  # play microwave pulse
            # measure('readout', 'APD', None, time_tagging.analog(times, 4 * cw_time_cycles, counts))
            assign(total_counts, total_counts + counts)
        save(total_counts, counts_st)
        assign(total_counts, 0)

    with stream_processing():
        counts_st.with_timestamps().save('counts')
#####################################
#  Open Communication with the QOP  #
#####################################
qmm = QuantumMachinesManager(host="192.168.1.254", port='80')

def measurement(qm, fig, it, prev_counts, prev_iterations):
    job = qm.execute(time_rabi)
    # Get results from QUA program
    res_handles = job.result_handles
    times_handle = res_handles.get("counts")
    iteration_handle = res_handles.get("iteration")
    times_handle.wait_for_values(1)
    iteration_handle.wait_for_values(1)
    results = fetching_tool(job, data_list=["counts", "iteration"], mode="live")
    # Live plotting
    interrupt_on_close(fig, job)  # Interrupts the job when closing the figure

    while results.is_processing():
        # Fetch results
        counts, iteration = results.fetch_all()
        counts += prev_counts
        iteration += prev_iterations
        # counts = times_handle.fetch_all()
        # iteration = iteration_handle.fetch_all()
        # Progress bar
        progress_counter(iteration, n_avg, start_time=results.get_start_time())
        # Plot data
        plt.cla()
        plt.plot(4 * t_vec, counts / it / 1000 / (meas_len / 1e9))  # u.s))
        plt.xlabel("Tau [ns]")
        plt.ylabel("Intensity [kcps]")
        plt.title("Time Rabi")
        plt.pause(0.1)
    job.halt()
    return counts, iteration
simulate = False
if simulate:
    simulation_config = SimulationConfig(duration=28000)
    job = qmm.simulate(config, time_rabi, simulation_config)
    job.get_simulated_samples().con1.plot()
else:
    qm = qmm.open_qm(config)
    counts = np.zeros(len(t_vec))
    iteration = 0
    fig = plt.figure()
    i = 0
    while 1:
        i += 1
        counts, iteration = measurement(qm, fig, i, counts, iteration)
        job_optim = qm.execute(counter)
        command = 'optimizerlogic.start_refocus(scannerlogic.get_position(), "confocalgui")'
        run_kernel_command(cmd=command, wait=10)
        job_optim.halt()

    # execute QUA program
    qm.close()