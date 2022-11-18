import matplotlib.pyplot as plt
from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
from configuration import *


################################

# Open quantum machine manager #
################################

qmm = QuantumMachinesManager(host="192.168.1.254", port='80')
#
# ########################
# # Open quantum machine #
# ########################
#

listOfMachines = qmm.list_open_quantum_machines() # Get ids of all the machine
machineId = ''
if len(listOfMachines)>0:
    for l in listOfMachines:
        qm = qmm.get_qm(l) # Get config corresponding to a machine
        configOfRunning = qm.get_config()
        controllers = configOfRunning['controllers']
        controllersElements = controllers['con1']
        digitalPorts = controllersElements['digital_outputs']
        # Check if digital port 5 is a part of our config because that is our machine
        if 1 in digitalPorts:
            machineId = l

    ################################
    # Get the job #
    ################################
    try:
        qm = qmm.get_qm(machineId)
        configOfRunning=qm.get_config()
        job = qm.get_running_job()
        if job is not None:
            job.halt()
        qm.close()
    except:
        print('Keine QM mit entsprechenden Ports gefunden.')
qmm.close()