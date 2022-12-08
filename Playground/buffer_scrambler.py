"""
Short script to write a buffer with 100 entries with corresponding index to check for validity of the save() and stream_processing() functions.
"""
from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
from qm import generate_qua_script
from configuration import config
from lib.sequences import *

with program() as buffer_test:
    N = declare(int)
    i = declare(int)
    a_st = declare_stream()  # Buffer stream
    i_st = declare_stream()  # Stream to output number of iterations separately

    with for_(i, 0, i < 10000000, i + 1):
        with for_(N, 0, N < 100, N + 1):
            save(N, a_st)
            wait(40)

        # Waiting time after writing all entries in the buffer. I was able to observe the buffer shift
        # at up to 20µs waiting time. Did not proceed with increased waiting time, since measurements take too long with
        # this high delay. Longer times increase the number of iterations it takes for an error to occur.
        # wait(20000 // 4)

    with stream_processing():
        a_st.buffer(100).save('array')
        #a_st.buffer(2, 100).save('array')
        #a_st.buffer(2).buffer(100).save('array')



# Comment this out and create a Manager and Machine instance
qmm, qm = setup_qm()
#####

job = qm.execute(buffer_test)
res_handles = job.result_handles
arr_handle = res_handles.get('array')
while arr_handle.is_processing():
    arr = arr_handle.fetch_all()
    try:
        check = [(arr[i] != i) for i in range(len(arr))]
        if any(check):
            print(f'WRONG BUFFER {arr}')
        else:
            print(f'CORRECT BUFFER {arr}')
    except:
        pass


# Serialize the file:
#sourceFile = open('debug.py', 'w')
#print(generate_qua_script(buffer_test, config), file=sourceFile)
#sourceFile.close()