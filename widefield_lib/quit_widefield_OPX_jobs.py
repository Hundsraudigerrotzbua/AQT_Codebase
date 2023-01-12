import matplotlib.pyplot as plt
from Playground.trigger_and_sweep_windfreak import OPX_MW
from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
from configuration_widefield import *


MW = OPX_MW()
MW.activate()
MW.off()
MW.deactivate()
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
        if 2 in digitalPorts or 1 in digitalPorts:
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
