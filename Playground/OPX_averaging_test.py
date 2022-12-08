from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
from lib.data_handler import *
from lib.sequences import *
from qualang_tools.plot import interrupt_on_close
from qualang_tools.results import progress_counter, fetching_tool
from configuration import *



n_avg = 5
c = np.round(np.random.randn(10), 3)*10
with program() as avgtest:
    counts = declare(int)  # variable for number of counts
    counts_st = declare_stream()  # stream for counts
    counts_st1 = declare_stream()  # stream for counts
    counts_st2 = declare_stream()  # stream for counts
    counts_st3 = declare_stream()  # stream for counts
    counts_st4 = declare_stream()  # stream for counts
    i = declare(int)  # variable to for_loop
    k = declare(int)
    n = declare(int)  # number of iterations
    n_st = declare_stream()  # stream for counts


    with for_(i, 0, i < 40, i + 1):
        with if_(modulo(i, 10) == 0):
            save(i, n_st)
        wait(100000000//4)

    with stream_processing():
        n_st.save("iteration")


qmm, qm = setup_qm()
job = qm.execute(avgtest)
results = fetching_tool(job, data_list=["iteration"], mode="live")
while results.is_processing():
    iteration = results.fetch_all()
    print(f'{iteration}')
job.halt()
qm.close()