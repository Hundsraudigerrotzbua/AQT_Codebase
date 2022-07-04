from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
import numpy as np
import os
import matplotlib.pyplot as plt
from configuration import config
#from QuantumMachines.Config_OPX1_24062020 import config
#from QuantumMachines.analysis.odmr_analysis import fit_odmr, n_lorentzians
#from QuantumMachines.analysis.fitting import find_peaks, fit_rabi
# import matplotlib as mpl
# mpl.use('Qt5Agg')

save_path = 'C:/Data/Temp_QM_Data/2020/06/20200614/'

IF_freq = 1.5e6
LO_freq = 2.813479e9-IF_freq

qmm = QuantumMachinesManager(host="192.168.1.254", port='80')
qm = qmm.open_qm(config)

def time_rabi_prog(RF_freq, RF_power, t_len=41, t_stop=404, rep_num=500000, f=0, fit=False, savefile=False, number = '004' , save_path = save_path):
    """
    :param t_len:
    :param t_stop:
    :param rep_num:
    :param f: The IQ modulation frequency (IF) and so RF = IF + LO (for SSB modulation)
              IF can be important so as not to cross other transitions...
    :return:
    """
    meas_len = 2000
    # t_len = 45
    # turn on the microwave at (RF_freq - f) and possibly refocus
    t_vec = [int(t_) for t_ in np.linspace(4, t_stop, t_len)]

    with program() as time_rabi:
        update_frequency('qubit', int(f))
        n = declare(int)
        m = declare(int)
        t = declare(int)
        result1 = declare(int, size=int(meas_len / 500))
        result_len1 = declare(int)
        result2 = declare(int, size=int(meas_len / 500))
        result_len2 = declare(int)
        rabi_vec = declare(int, size=t_len)
        t_ind = declare(int)

        play('rabi', 'laser', duration=3000 // 4)

        with for_(n, 0, n < rep_num, n + 1):
            assign(t_ind, 0)
            with for_each_(t, t_vec):
                # wait(100 // 4, 'qubit')
                play('pi', 'NV', duration=t)
                align('NV', 'APD', 'APD2', 'AOM')
                readout_qua(result1, result2, result_len1, result_len2, meas_len, rabi_vec, t_ind, m)
                assign(t_ind, t_ind + 1)

        with for_(t_ind, 0, t_ind < rabi_vec.length(), t_ind+1):
            save(rabi_vec[t_ind], 'rabi')

    # job = qm.simulate(time_rabi, SimulationConfig(20000))
    # res = job.get_simulated_samples()
    job = qm.execute(time_rabi, duration_limit=0, data_limit=0, force_execution=True)
    res_handles = job.result_handles
    res_handles.wait_for_all_values()
    counts_handle = res_handles.get('rabi')
    counts = counts_handle.fetch_all()['value']
    plt.figure()
    taus = np.linspace(4, t_stop, t_len)*4
    c = counts/counts.max()
    plt.plot(taus, c)
    plt.xlabel(r'$\tau$ [ns]')
    plt.ylabel('normalized contrast')
    rabi_str = 'rabi/' + 'rabi_' + str(number)
    power_str = '_power= ' + str(RF_power) + '_dBm'
    filename = save_path + rabi_str + power_str + '.dat'  # need an automatic numbering system
    # turn off microwave
    if fit:
        pass
        #p, v, q, chi = fit_rabi(taus, c, c**0.5, decay=True)
        #x = np.linspace(taus[0], taus[-1], 300)  # needs to choose # of points in a more intelligent way
        #y = np.exp(-x/p[4])*p[0]*np.cos(2*np.pi*(x-p[2])/p[1]) + p[3]
        #plt.plot(x, y)
        #plt.legend(('data', 'fit'))
        #contrast = int(1e2*(y.max()-y.min()))
        #plt.title('Rabi period = ' + str(round(p[1],0)) + ' ns, contrast = ' + str(contrast) + '%')
        #t_pi = p[1]/2
        #t_pi2 = t_pi/2
        #plt.savefig(filename + '.png')
    else:
        plt.savefig(filename + '.png')
        t_pi = 100
        print('not a fitted t-pi!')  # !!!no fit!!!
    if savefile:
        m = np.array((taus, c))
        power_str = 'power = ' + str(RF_power) + 'dBm, '
        freq_str = 'freq = ' + str(RF_freq/1e9) + ' GHz, '
        mod_str = 'modulation = ' + str(f/1e6) + ' MHz'
        file_header = power_str + freq_str + mod_str
        if not os.path.exists('filename'):
            np.savetxt(filename, m.T, delimiter='\t', header=file_header)
        else:
            print('filename ' + filename + ' already exists')
    return taus, c, t_pi

def readout_qua(result1, result2, result_len1, result_len2, meas_len, rabi_vec, t_ind, m):

    wait(100 // 4, 'laser')
    play('rabi', 'laser', duration=(meas_len - 400) // 4)
    measure('rabi', 'readout1', None, time_tagging.raw(result1, meas_len, targetLen=result_len1))
    measure('rabi', 'readout2', None, time_tagging.raw(result2, meas_len, targetLen=result_len2))  # 1ns

    with for_(m, 0, m < result_len1, m + 1):
        with if_((result1[m] > 220) & (result1[m] < 400)):
            assign(rabi_vec[t_ind], rabi_vec[t_ind] + 1)

    with for_(m, 0, m < result_len2, m + 1):
        with if_((result2[m] > 220) & (result2[m] < 400)):
            assign(rabi_vec[t_ind], rabi_vec[t_ind] + 1)
