from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
import numpy as np
import os
from qm import SimulationConfig
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import time
from QuantumMachines.Config_OPX1_24062020 import config
from QuantumMachines.analysis.odmr_analysis import fit_odmr, n_lorentzians
from QuantumMachines.analysis.fitting import find_peaks, fit_rabi
from qm.qua import math
# import matplotlib as mpl
# mpl.use('Qt5Agg')

save_path = 'C:/Data/Temp_QM_Data/2020/06/20200614/'

IF_freq = 1.5e6
LO_freq = 2.813479e9-IF_freq

qmm = QuantumMachinesManager()
qm = qmm.open_qm(config)
