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

###################
# The QUA program #
###################

t_min = 16 // 4  # in clock cycles units (must be >= 4)
t_max = 2000 // 4  # in clock cycles units
dt = 150 // 4  # in clock cycles units
t_vec = np.arange(t_min, t_max + 0.1, dt)  # +0.1 to include t_max in array
n_avg = 1e6

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

#####################################
#  Open Communication with the QOP  #
#####################################
qmm = QuantumMachinesManager(host="192.168.1.254", port='80')

simulate = False
if simulate:
    simulation_config = SimulationConfig(duration=28000)
    job = qmm.simulate(config, time_rabi, simulation_config)
    job.get_simulated_samples().con1.plot()
else:
    qm = qmm.open_qm(config)
    # execute QUA program
    job = qm.execute(time_rabi)
    # Get results from QUA program
    res_handles = job.result_handles
    times_handle = res_handles.get("counts")
    iteration_handle = res_handles.get("iteration")
    times_handle.wait_for_values(1)
    iteration_handle.wait_for_values(1)
    results = fetching_tool(job, data_list=["counts", "iteration"], mode="live")
    # Live plotting
    fig = plt.figure()
    interrupt_on_close(fig, job)  # Interrupts the job when closing the figure

    while results.is_processing():
        # Fetch results
        counts, iteration = results.fetch_all()
        #counts = times_handle.fetch_all()
        #iteration = iteration_handle.fetch_all()
        # Progress bar
        progress_counter(iteration, n_avg, start_time=results.get_start_time())
        # Plot data
        plt.cla()
        plt.plot(4 * t_vec, counts / 1000 / (meas_len / 1e9)) #u.s))
        plt.xlabel("Tau [ns]")
        plt.ylabel("Intensity [kcps]")
        plt.title("Time Rabi")
        plt.pause(0.1)
    qm.close()