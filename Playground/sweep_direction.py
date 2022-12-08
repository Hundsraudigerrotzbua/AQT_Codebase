"""
Short script to write a buffer with 100 entries with corresponding index to check for validity of the save() and stream_processing() functions.
"""
from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
from lib.sequences import *
from configuration import config

f = list(range(100, 110))
# [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
with program() as buffer_test:
    i = declare(int)
    arr = declare(int, value=f)
    i_st = declare_stream()  # Stream to output number of iterations separately

    with for_(i, 9, i >= 0, i - 1):
            save(arr[i], i_st)

        # Waiting time after writing all entries in the buffer. I was able to observe the buffer shift
        # at up to 20µs waiting time. Did not proceed with increased waiting time, since measurements take too long with
        # this high delay. Longer times increase the number of iterations it takes for an error to occur.
        # wait(20000 // 4)

    with stream_processing():
        i_st.buffer(10).save('array')

qmm, qm = setup_qm()

job = qm.execute(buffer_test)
res_handles = job.result_handles
arr_handle = res_handles.get('array')
while arr_handle.is_processing():
    arr = arr_handle.fetch_all()
    print(arr)
