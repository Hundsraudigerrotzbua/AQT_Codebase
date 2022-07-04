import matplotlib.pyplot as plt
from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *

from configuration import *
qmm = QuantumMachinesManager(host="192.168.1.254", port='80')

qm = qmm.open_qm(config)

with program() as dummy:
    signal = declare(int)  # saves number of photon counts
job = qm.execute(dummy)
job.halt()
qm.close()
