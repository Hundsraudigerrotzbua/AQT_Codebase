import numpy as np


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
