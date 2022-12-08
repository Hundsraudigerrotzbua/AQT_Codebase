import numpy as np
from lib.sequences import *
import time


def vp_to_dbm(vp):
    """
    Convert Peak Voltages to dBm Powers.
    """
    return 10 + 20 * np.log10(vp)


def dbm_to_vp(dbm):
    """
    Convert dBm Powers to Peak Voltages.
    """
    return 10 ** ((dbm - 10) / 20)


def defect_holder():
    with program() as counter:
        with infinite_loop_():
            play('laser_ON', 'AOM', duration=int(3000 // 4))

    qmm, qm = setup_qm()
    while 1:
        job_optim = qm.execute(counter)
        command = 'optimizerlogic.start_refocus(scannerlogic.get_position(), "confocalgui")'
        run_kernel_command(cmd=command, wait=10)
        job_optim.halt()
        time.sleep(600)
    return qmm.close()

