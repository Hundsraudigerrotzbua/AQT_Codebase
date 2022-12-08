from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
from qm import generate_qua_script
from configuration import config
from lib.sequences import *


t_min = 16  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
t_max = 3000  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
dt =  100  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
n_avg= 1000
t_vec = np.arange(t_min//4, t_max//4 + 0.1, dt).tolist()

prev_counts = np.zeros(len(t_vec), dtype=np.int64)
prev_iterations = 0

with program() as time_rabi:
    counts = declare(int)  # variable for number of counts
    counts_st = declare_stream()  # stream for counts
    times = declare(int, size=100)
    n = declare(int)  # variable to for_loop
    i = declare(int)  # variable to for_loop
    n_st = declare_stream()  # stream to save iterations
    test_counts = declare(int, size=len(t_vec))
    times_vec = declare(int, value=[int(x) for x in t_vec])

    play("laser_ON", "AOM")
    wait(100, "AOM")
    with for_(n, 0, n < n_avg, n + 1):
        with for_(i, 0, i < test_counts.length(), i + 1):
            play("const", "NV", duration=times_vec[i])  # pulse of varied lengths
            align()
            play("laser_ON", "AOM")
            measure("readout", "APD", None, time_tagging.analog(times, meas_len, counts))
            assign(test_counts[i], counts + test_counts[i])
            save(test_counts[i], counts_st)  # save counts
            wait(100)
        save(n, n_st)  # save number of iteration inside for_loop

    with stream_processing():
        counts_st.buffer(len(t_vec)).save("counts")
        n_st.save("iteration")

qmm, qm = setup_qm()

job = qm.execute(time_rabi)
res_handles = job.result_handles
times_handle = res_handles.get("counts")
iteration_handle = res_handles.get("iteration")
times_handle.wait_for_values(1)
iteration_handle.wait_for_values(1)
results = fetching_tool(job, data_list=["counts", "iteration"], mode="live")
fig, ax = plt.subplots(1, 1)

interrupt_on_close(fig, job)  # Interrupts the job when closing the figure
while results.is_processing():
    counts, iteration = results.fetch_all()

    counts += prev_counts
    iteration += prev_iterations

    fig, ax = plot_rabi_live(t_vec, counts, lw=4, fig=fig, ax=ax,
                             elapsed_iterations=iteration)
job.halt()

#sourceFile = open('rabi_serialized.py', 'w')
#print(generate_qua_script(time_rabi, config), file=sourceFile)
#sourceFile.close()
