from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from configuration import *
from qm import SimulationConfig
import scipy.optimize as so
from lib.QuantechPlots import *


def readout(element, timestamps, length, counts, counts_stream):
    play('laser_ON', 'AOM')
    measure('readout', element, None,
            time_tagging.analog(timestamps, length, counts))
    save(counts, counts_stream)  # save counts


def end_sequence(job, qmm):
    job.halt()
    qmm.close()


def hahn_echo_decay_fit(x, y, T2_guess = 100):
    def func(x, a, b, c):
        return a * np.exp(-x / b) + c

    a, b = so.curve_fit(func, x, y, p0=(0.1, T2_guess, 1))
    return x, func(x, *a), a[1]


def hahn_echo(t_min, t_max, dt, n_avg=1e6, ampli=2, pulse_time=80, plot=1, fit=True, savefig=None):
    qmm = QuantumMachinesManager(host="192.168.1.254", port='80')
    qm = qmm.open_qm(config)
    t_vec = np.arange(t_min, t_max + 0.1, dt)  # +dt/2 to include t_max in array
    t_min //= 4
    t_max //= 4
    dt //= 4
    with program() as hahn_echo:
        counts1 = declare(int)  # saves number of photon counts
        counts2 = declare(int)  # saves number of photon counts
        counts_1_st = declare_stream()  # stream for counts
        counts_2_st = declare_stream()  # stream for counts
        timestamps_1 = declare(int, size=100)
        timestamps_2 = declare(int, size=100)
        t = declare(int)  # variable to sweep over in time
        n = declare(int)  # variable to for_loop
        n_st = declare_stream()  # stream to save iterations
        play('laser_ON', 'AOM')  # Photoluminescence
        wait(100)
        with for_(n, 0, n < n_avg, n + 1):
            with for_(t, t_min, t <= t_max, t + dt):
                reset_frame('NV')
                play('pi_half' * amp(ampli), 'NV', duration=pulse_time // 4 / 2)  # pulse of varied lengths
                wait(t / 2, 'NV')
                # frame_rotation_2pi(1/2, 'NV')
                play('pi' * amp(ampli), 'NV', duration=pulse_time // 4)  # pulse of varied lengths
                wait(t / 2, 'NV')
                play('pi_half' * amp(ampli), 'NV', duration=pulse_time // 4 / 2)  # pulse of varied lengths
                align()
                wait(4)
                readout('APD', timestamps_1, meas_len, counts1, counts_1_st)
                # play('laser_ON', 'AOM')
                # measure('readout', 'APD', None,
                #        time_tagging.analog(timestamps_1, meas_len, counts1))
                # save(counts1, counts_1_st)  # save counts
                wait(100)

                align()

                play('pi_half' * amp(ampli), 'NV', duration=pulse_time // 4 / 2)  # Pi/2 pulse to qubit
                wait(t, 'NV')  # variable delay in spin Echo
                play('pi' * amp(ampli), 'NV', duration=pulse_time // 4)  # Pi pulse to qubit
                wait(t, 'NV')  # variable delay in spin Echo
                frame_rotation_2pi(0.5, 'NV')
                play('pi_half' * amp(ampli), 'NV', duration=pulse_time // 4 / 2)  # Pi/2 pulse to qubit
                reset_frame('NV')
                align()
                readout('APD', timestamps_2, meas_len, counts2, counts_2_st)
                # play('laser_ON', 'AOM')
                # measure('readout', 'APD', None,
                #        time_tagging.analog(timestamps_2, meas_len, counts2))
                # save(counts2, counts_2_st)  # save counts
                wait(100)
            save(n, n_st)  # save number of iteration inside for_loop
        with stream_processing():
            counts_1_st.buffer(len(t_vec)).average().save('signal1')
            counts_2_st.buffer(len(t_vec)).average().save('signal2')
            n_st.save('iteration')
    job = qm.execute(hahn_echo)  # execute QUA program

    res_handle = job.result_handles  # get access to handles
    vec_handle1 = res_handle.get('signal1')
    vec_handle2 = res_handle.get('signal2')
    vec_handle1.wait_for_values(1)
    iteration_handle = res_handle.get('iteration')
    iteration_handle.wait_for_values(1)
    while vec_handle1.is_processing():
        if plot:
            try:
                signal1 = vec_handle1.fetch_all()
                signal2 = vec_handle2.fetch_all()
                iteration = iteration_handle.fetch_all() + 1
            except Exception as e:
                pass
            else:
                hahn_echo_plot(t_vec, signal1, signal2, T2_guess=100, fit=fit)
                #y = (np.abs(signal1 - signal2)) / np.max(signal1)
                #_, y_fit, T2 = hahn_echo_decay_fit(t_vec, y)
                #plt.plot(t_vec, y, 'o', label=f'Signal')  # / (meas_len*1e-9))
                #plt.plot(t_vec, y_fit, label=f'Exponential Fit')
                #plt.plot([T2, T2], [np.min(y), np.max(y)], 'k--', label=f'T2 = {np.around(T2, 1)} ns')
                #plt.xlabel('t [ns]')
                #plt.ylabel('Echo Signal')
                plt.title(f'Hahn Echo - {np.around(pi_amp_NV * ampli, 3)} Vpp; {int(iteration/n_avg * 100)}%')
                #plt.legend()
                plt.pause(0.1)
                plt.clf()

    signal1 = vec_handle1.fetch_all()
    signal2 = vec_handle2.fetch_all()
    iteration = iteration_handle.fetch_all() + 1
    if plot:
        hahn_echo_plot(t_vec, signal1, signal2, T2_guess=100, fit=fit)
        #y = (np.abs(signal1 - signal2)) / np.max(signal1)
        #_, y_fit, T2 = hahn_echo_decay_fit(t_vec, y)
        #plt.plot(t_vec, y, 'o', label=f'Signal')  # / (meas_len*1e-9))
        #plt.plot(t_vec, y_fit, label=f'Exponential Fit')
        #plt.plot([T2, T2], [np.min(y), np.max(y)], 'k--', label=f'T2 = {np.around(T2, 1)} ns')
        #plt.xlabel('t [ns]')
        #plt.ylabel('Echo Signal')
        plt.title(f'Hahn Echo - {np.around(pi_amp_NV * ampli, 3)} Vpp; {int(iteration / n_avg * 100)}%')
        #plt.legend()
        if savefig is not None:
            plt.savefig(savefig + '.png')
    end_sequence(job, qmm)
    return t_vec, signal1, signal2, iteration


def ramsey(t_min, t_max, dt, n_avg=1e6, ampli=2, pulse_time=80, plot=1, savefig=None):
    qmm = QuantumMachinesManager(host="192.168.1.254", port='80')
    qm = qmm.open_qm(config)
    t_vec = np.arange(t_min, t_max + 0.5, dt)  # +dt/2 to include t_max in array
    t_min //= 4
    t_max //= 4
    dt //= 4
    with program() as ramsey:
        counts1 = declare(int)  # saves number of photon counts
        counts2 = declare(int)  # saves number of photon counts
        counts_1_st = declare_stream()  # stream for counts
        counts_2_st = declare_stream()  # stream for counts
        timestamps_1 = declare(int, size=100)
        timestamps_2 = declare(int, size=100)
        t = declare(int)  # variable to sweep over in time
        n = declare(int)  # variable to for_loop
        n_st = declare_stream()  # stream to save iterations
        play('laser_ON', 'AOM')  # Photoluminescence
        with for_(n, 0, n < n_avg, n + 1):
            with for_(t, t_min, t <= t_max, t + dt):
                play('pi_half' * amp(ampli), 'NV', duration=pulse_time // 4 / 2)  # pulse of varied lengths
                wait(t, 'NV')
                play('pi_half' * amp(ampli), 'NV', duration=pulse_time // 4 / 2)  # pulse of varied lengths
                align()
                wait(4)
                readout('APD', timestamps_1, meas_len, counts1, counts_1_st)
                # play('laser_ON', 'AOM')
                # measure('readout', 'APD', None,
                #        time_tagging.analog(timestamps_1, meas_len, counts1))
                # save(counts1, counts_1_st)  # save counts
                wait(10)
                align()
                play('pi_half' * amp(ampli), 'NV', duration=pulse_time // 4 / 2)  # pulse of varied lengths
                wait(t, 'NV')
                frame_rotation_2pi(0.5, 'NV')
                play('pi_half' * amp(ampli), 'NV', duration=pulse_time // 4 / 2)  # pulse of varied lengths
                align()
                wait(4)
                readout('APD', timestamps_2, meas_len, counts2, counts_2_st)
                # play('laser_ON', 'AOM')
                # measure('readout', 'APD', None,
                #        time_tagging.analog(timestamps_2, meas_len, counts2))
                # save(counts2, counts_2_st)  # save counts
                wait(10)
            save(n, n_st)  # save number of iteration inside for_loop
        with stream_processing():
            counts_1_st.buffer(len(t_vec)).average().save('signal1')
            counts_2_st.buffer(len(t_vec)).average().save('signal2')
            n_st.save('iteration')
    job = qm.execute(ramsey)  # execute QUA program
    res_handle = job.result_handles  # get access to handles
    vec_handle1 = res_handle.get('signal1')
    vec_handle2 = res_handle.get('signal2')
    vec_handle1.wait_for_values(1)
    iteration_handle = res_handle.get('iteration')
    iteration_handle.wait_for_values(1)
    while vec_handle1.is_processing():
        if plot:
            try:
                signal1 = vec_handle1.fetch_all()
                signal2 = vec_handle2.fetch_all()
                iteration = iteration_handle.fetch_all() + 1
            except Exception as e:
                pass
            else:
                plt.plot(t_vec, (signal1 - signal2) / (meas_len * 1e-9))
                plt.xlabel('t [ns]')
                plt.ylabel('Signal [cps]')
                plt.title(f'Ramsey - {pi_amp_NV * ampli} Vpp; {iteration} Iters')
                plt.pause(0.1)
                plt.clf()
    signal1 = vec_handle1.fetch_all()
    signal2 = vec_handle2.fetch_all()
    if plot:
        plt.plot(t_vec, (signal1 - signal2) / (meas_len * 1e-9))
        plt.xlabel('t [ns]')
        plt.ylabel('Signal [cps]')
        plt.title(f'Ramsey - {pi_amp_NV * ampli} Vpp; {iteration} Iters')
        if savefig is not None:
            plt.savefig(savefig + '.png')
    end_sequence(job, qmm)
    return t_vec, signal1, signal2, iteration


def rabi(t_min, t_max, dt, n_avg=1e6, ampli=2, plot=1, savefig=None):
    t_vec = np.arange(t_min, t_max + 0.5, dt)  # +dt/2 to include t_max in array
    qmm = QuantumMachinesManager(host="192.168.1.254", port='80')
    qm = qmm.open_qm(config)
    t_min //= 4
    t_max //= 4
    dt //= 4

    def normalization(counts_1_st, counts_2_st):
        counts_1 = declare(int)
        counts_2 = declare(int)
        timestamps1 = declare(int, size=100)
        timestamps2 = declare(int, size=100)
        play('laser_ON', 'AOM')
        measure('readout', 'APD', None,
                time_tagging.analog(timestamps1, meas_len, counts_1))
        wait((laser_len - 3 * meas_len) // 4, 'APD2')
        measure('readout', 'APD2', None,
                time_tagging.analog(timestamps2, meas_len, counts_2))
        save(counts_1, counts_1_st)
        save(counts_2, counts_2_st)

    with program() as time_rabi:

        counts_1_st = declare_stream()  # stream for counts
        counts_2_st = declare_stream()  # stream for counts
        t = declare(int)  # variable to sweep over in time
        n = declare(int)  # variable to for_loop
        n_st = declare_stream()  # stream to save iterations
        play('laser_ON', 'AOM')  # Photoluminescence
        with for_(n, 0, n < n_avg, n + 1):
            with for_(t, t_min, t <= t_max, t + dt):
                play('pi' * amp(ampli), 'NV', duration=t)  # pulse of varied lengths
                align()
                wait(4)
                normalization(counts_1_st, counts_2_st)
                wait(100)
            save(n, n_st)  # save number of iteration inside for_loop
        with stream_processing():
            counts_1_st.buffer(len(t_vec)).average().save('signal1')
            counts_2_st.buffer(len(t_vec)).average().save('signal2')
            n_st.save('iteration')
    job = qm.execute(time_rabi)  # execute QUA program
    res_handle = job.result_handles  # get access to handles
    vec_handle1 = res_handle.get('signal1')
    vec_handle2 = res_handle.get('signal2')
    vec_handle1.wait_for_values(1)
    iteration_handle = res_handle.get('iteration')
    iteration_handle.wait_for_values(1)
    fig = plt.figure()
    ax = plt.gca()
    ax2 = ax.twinx()
    while vec_handle1.is_processing():
        if plot:
            try:
                signal1 = vec_handle1.fetch_all()
                signal2 = vec_handle2.fetch_all()
                iteration = iteration_handle.fetch_all() + 1
            except Exception as e:
                pass
            else:
                pl1 = ax.plot(t_vec, signal1, color='blue', label='Signal1')
                pl2 = ax.plot(t_vec, signal2, color='red', label='Signal2')
                pl3 = ax2.plot(t_vec, signal1 / signal2, color='k', label='Signal1/Signal2')
                ax.set_xlabel('t [ns]')
                ax.set_ylabel('Signal 1 and 2')
                ax2.set_ylabel('Signal1/Signal2')
                plt.title(f'Time Rabi normalized at {pi_amp_NV * ampli} V; {iteration} Iters')
                ln = pl1 + pl2 + pl3
                labs = [l.get_label() for l in ln]
                plt.legend(ln, labs, loc=0)
                plt.pause(0.1)
                ax.clear()
                ax2.clear()

    signal1 = vec_handle1.fetch_all()
    signal2 = vec_handle1.fetch_all()
    if plot:
        pl1 = ax.plot(t_vec, signal1, color='blue', label='Signal1')
        pl2 = ax.plot(t_vec, signal2, color='red', label='Signal2')
        pl3 = ax2.plot(t_vec, signal1 / signal2, color='k', label='Signal1/Signal2')
        ln = pl1 + pl2 + pl3
        labs = [l.get_label() for l in ln]
        plt.legend(ln, labs, loc=0)
        ax.set_xlabel('t [ns]')
        ax.set_ylabel('Signal 1 and 2')
        ax2.set_ylabel('Signal1/Signal2')
        plt.title(f'Time Rabi normalized at {np.around(pi_amp_NV * ampli, 3)} V; {iteration} Iters')
        plt.legend()
        if savefig is not None:
            plt.savefig(savefig + '.png')
    end_sequence(job, qmm)
    return t_vec, signal1, signal2, iteration
