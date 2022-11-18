from qm.QuantumMachinesManager import QuantumMachinesManager
from configuration import *
from qm.qua import *
from lib.qudi_communication import run_kernel_command
import time

######################################################
###### Script to trap a vacancy in the optimizer #####
######################################################

total_time = 0.1  # 100ms
cw_time_sec = 50e-6  # 50us
cw_time_cycles = int(cw_time_sec * 1e9 // 4)
n_count = int(total_time / cw_time_sec)

with program() as counter:
    with infinite_loop_():
        play('laser_ON', 'AOM', duration=int(3000 // 4))
        # play('const', 'NV', duration=int(3000// 4))  # play microwave pulse

qmm = QuantumMachinesManager(host="192.168.1.254", port='80')
qm = qmm.open_qm(config, close_other_machines=False)

while 1:
    job_optim = qm.execute(counter)
    command = 'optimizerlogic.start_refocus(scannerlogic.get_position(), "confocalgui")'
    run_kernel_command(cmd=command, wait=10)
    job_optim.halt()
    time.sleep(600)
qmm.close()
