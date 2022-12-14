import datetime
import time
from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
from qm import SimulationConfig
from configuration import *
from qualang_tools.plot import interrupt_on_close
from qualang_tools.results import progress_counter, fetching_tool
from lib.qudi_communication import run_kernel_command
from lib.data_handler import *


def cw_odmr(qmm, qm, fig, settings, prev_counts, prev_iterations, simulate=False, ax=None):
    """
    Continuous Wave ODMR Sequence
    :param qmm: Quantum Machines Manager Instance
    :param qm: Quantum Machine to perform measurement in.
    :param fig: Pyplot Figure handle to plot the live image in.
    :param settings: The specified measurement settings.
    :param prev_counts: The measured photon counts of the previous iteration.
    :param prev_iterations: The current iterations at the start of this measurement run.
    :param simulate: Simulation Flag.
    :param ax: Pyplot axis to plot in.
    :return: Current photon counts, current measurement iteration.
    """
    f_vec = settings['f_vec']
    if 'n_avg' not in settings and 'optimizer_interval' in settings:
        n_avg = settings['optimizer_interval'] / (len(f_vec) * odmr_meas_len * 1e-9)
    elif ('n_avg' in settings and 'optimizer_interval' not in settings) or ('n_avg' in settings and 'optimizer_interval' in settings):
        n_avg = settings['n_avg']
    else:
        raise ValueError(f'Neither averages nor optimizer interval given to sequence!')

    with program() as cwodmr:
        counts_val = declare(int)  # variable for number of counts
        counts_st = declare_stream()  # stream for counts
        timestamps = declare(int, size=1000)
        i = declare(int)  # variable to for_loop
        n = declare(int)  # number of iterations
        n_st = declare_stream()  # stream for number of iterations
        test_counts = declare(int, size=len(f_vec))
        freq_vec = declare(int, value=[int(x) for x in f_vec])

        with for_(n, 0, n < n_avg, n + 1):
            #with for_(i, test_counts.length()-1, i >= 0, i - 1):
            with for_(i, 0, i < test_counts.length(), i + 1):
                update_frequency('NV', freq_vec[i])  # updated frequency
                align()  # align all elements
                play('const', 'NV', duration=int(odmr_meas_len // 4))  # play microwave pulse
                play('laser_ON', 'AOM', duration=int(odmr_meas_len // 4))  # Photoluminescence
                measure('readout_cw', 'APD', None,
                        time_tagging.analog(timestamps, odmr_meas_len, counts_val))
                assign(test_counts[i], counts_val + test_counts[i])
                save(test_counts[i], counts_st)
                wait(500)
            save(n, n_st)  # save number of iteration inside for_loop

        with stream_processing():
            counts_st.buffer(len(f_vec)).average().save("counts")
            n_st.save("iteration")

    if simulate:
        simulation_config = SimulationConfig(duration=28000)
        job = qmm.simulate(config, cwodmr, simulation_config)
        job.get_simulated_samples().con1.plot()
        interrupt_on_close(fig, job)  # Interrupts the job when closing the figure
        return np.zeros(len(f_vec)), 0
    else:
        job = qm.execute(cwodmr)
        #print('Grabbing Handle')
        #res_handles = job.result_handles
        #print('Grabbing counts handle')
        #times_handle = res_handles.get("counts")
        #print('Grabbing iteration handle')
        #iteration_handle = res_handles.get("iteration")
        #print('Waiting for times value')
        #times_handle.wait_for_values(1)
        #print('Waiting for iteration value')
        #iteration_handle.wait_for_values(1)
        results = fetching_tool(job, data_list=["counts", "iteration"], mode="live")
        interrupt_on_close(fig, job)  # Interrupts the job when closing the figure
        while results.is_processing():
            counts, iteration = results.fetch_all()

            counts += prev_counts
            iteration += prev_iterations

            _, _ = plot_odmr_live(f_vec, counts, lw=4, fig=fig, AX=ax,
                                  elapsed_iterations=iteration)
        job.halt()
        return counts, iteration

def cw_odmr_with_qua_syntax(qmm, qm, fig, settings, prev_counts, prev_iterations, simulate=False, ax=None):
    """
    Continuous Wave ODMR Sequence
    :param qmm: Quantum Machines Manager Instance
    :param qm: Quantum Machine to perform measurement in.
    :param fig: Pyplot Figure handle to plot the live image in.
    :param settings: The specified measurement settings.
    :param prev_counts: The measured photon counts of the previous iteration.
    :param prev_iterations: The current iterations at the start of this measurement run.
    :param simulate: Simulation Flag.
    :param ax: Pyplot axis to plot in.
    :return: Current photon counts, current measurement iteration.
    """
    #'f_min': 2.85e9,  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
    #'f_max': 2.89e9,  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
    #'df': 2e6,  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
    f_vec = settings['f_vec']
    f_min = 280e6#settings['f_min']
    f_max = 320e6#settings['f_max']
    df = 2e6#settings['df']
    f_vec = np.arange(f_min, f_max + 0.1, df)
    if 'n_avg' not in settings and 'optimizer_interval' in settings:
        n_avg = settings['optimizer_interval'] / (len(f_vec) * odmr_meas_len * 1e-9)
    elif ('n_avg' in settings and 'optimizer_interval' not in settings) or ('n_avg' in settings and 'optimizer_interval' in settings):
        n_avg = settings['n_avg']
    else:
        raise ValueError(f'Neither averages nor optimizer interval given to sequence!')

    with program() as cwodmr:
        counts_val = declare(int)  # variable for number of counts
        counts_st = declare_stream()  # stream for counts
        timestamps = declare(int, size=1000)
        #i = declare(int)  # variable to for_loop
        f = declare(int)  # variable to for_loop
        n = declare(int)  # number of iterations
        n_st = declare_stream()  # stream for number of iterations
        #test_counts = declare(int, size=len(f_vec))
        #freq_vec = declare(int, value=[int(x) for x in f_vec])

        with for_(n, 0, n < n_avg, n + 1):
            #assign(i, 0)
            with for_(f, f_max, f >= f_min, f - df):
                #with for_(i, test_counts.length()-1, i >= 0, i - 1):
                update_frequency('NV', f)  # updated frequency
                align()  # align all elements
                play('const', 'NV', duration=int(odmr_meas_len // 4))  # play microwave pulse
                play('laser_ON', 'AOM', duration=int(odmr_meas_len // 4))  # Photoluminescence
                measure('readout_cw', 'APD', None,
                        time_tagging.analog(timestamps, odmr_meas_len, counts_val))
                save(counts_val, counts_st)
                #assign(test_counts[i], counts_val + test_counts[i])
                #save(test_counts[i], counts_st)
                #assign(i, i+1)
            #save(n, n_st)  # save number of iteration inside for_loop

        with stream_processing():
            counts_st.buffer(len(f_vec)).average().save("counts")
            #n_st.save("iteration")

    if simulate:
        simulation_config = SimulationConfig(duration=28000)
        job = qmm.simulate(config, cwodmr, simulation_config)
        job.get_simulated_samples().con1.plot()
        interrupt_on_close(fig, job)  # Interrupts the job when closing the figure
        return np.zeros(len(f_vec)), 0
    else:
        job = qm.execute(cwodmr)
        #print('Grabbing Handle')
        #res_handles = job.result_handles
        #print('Grabbing counts handle')
        #times_handle = res_handles.get("counts")
        #print('Grabbing iteration handle')
        #iteration_handle = res_handles.get("iteration")
        #print('Waiting for times value')
        #times_handle.wait_for_values(1)
        #print('Waiting for iteration value')
        #iteration_handle.wait_for_values(1)
        results = fetching_tool(job, data_list=["counts"], mode="live")
        interrupt_on_close(fig, job)  # Interrupts the job when closing the figure
        while results.is_processing():
            counts = results.fetch_all()

            #counts += prev_counts
            #iteration += prev_iterations

            plt.plot(f_vec, counts[0])
            plt.pause(0.1)
            plt.clf()

            #_, _ = plot_odmr_live(f_vec, counts, lw=4, fig=fig, AX=ax,
            #                      elapsed_iterations=iteration)
        job.halt()
        return counts, #iteration




def time_rabi(qmm, qm, fig, settings, frequency=None, amplitude=1, prev_counts=0, prev_iterations=0, simulate=False,
                    ax=None):
    """
    Rabi measurement that will sweep the duration of the microwave signal.
    :param qmm: Quantum Machines Manager Instance
    :param qm: Quantum Machine to perform measurement in.
    :param fig: Pyplot Figure handle to plot the live image in.
    :param settings: The specified measurement settings.
    :param frequency: Frequency of the I-Q output for the microwave signal.
    :param amplitude: Amplitude of the microwave signal. (Only values between -2 and 2-2**-16 are valid).
    :param prev_counts: The measured photon counts of the previous iteration.
    :param prev_iterations: The current iterations at the start of this measurement run.
    :param simulate: Simulation Flag.
    :param ax: Pyplot axis to plot in.
    :return: Current photon counts, current measurement iteration.
    """
    t_vec = settings['t_vec']  # +0.1 to include t_max in array
    if 'n_avg' not in settings and 'optimizer_interval' in settings:
        n_avg = settings['optimizer_interval'] / (6*len(t_vec) * (np.mean(t_vec) + meas_len + 100)* 1e-9)
    elif ('n_avg' in settings and 'optimizer_interval' not in settings) or ('n_avg' in settings and 'optimizer_interval' in settings):
        n_avg = settings['n_avg']
    else:
        raise ValueError(f'Neither averages nor optimizer interval given to sequence!')
    if frequency is None:
        frequency = NV_IF_freq
    with program() as time_rabi:
        counts = declare(int)  # variable for number of counts
        counts_st = declare_stream()  # stream for counts
        times = declare(int, size=100)
        n = declare(int)  # variable to for_loop
        i = declare(int)  # variable to for_loop
        c = declare(int)
        n_st = declare_stream()  # stream to save iterations
        test_counts = declare(int, size=len(t_vec))
        times_vec = declare(int, value=[int(x) for x in t_vec])

        play("laser_ON", "AOM")
        wait(100, "AOM")
        with for_(n, 0, n < n_avg, n + 1):
            with for_(i, 0, i < test_counts.length(), i + 1):
                update_frequency('NV', frequency)
                play("const" * amp(amplitude), "NV", duration=times_vec[i])  # pulse of varied lengths
                align()
                play("laser_ON", "AOM")
                measure("readout", "APD", None, time_tagging.analog(times, meas_len, counts))
                assign(test_counts[i], counts + test_counts[i])
                save(test_counts[i], counts_st)  # save counts
                wait(100)
            save(n, n_st)  # save number of iteration inside for_loop

        with for_each_(c, test_counts):
            save(c, 'rabi')
        with stream_processing():
            counts_st.buffer(len(t_vec)).save("counts")
            n_st.save("iteration")
    if simulate:
        simulation_config = SimulationConfig(duration=28000)
        job = qmm.simulate(config, time_rabi, simulation_config)
        job.get_simulated_samples().con1.plot()
        interrupt_on_close(fig, job)  # Interrupts the job when closing the figure
        return np.zeros(len(t_vec)), 0
    else:
        job = qm.execute(time_rabi)
        res_handles = job.result_handles
        times_handle = res_handles.get("counts")
        iteration_handle = res_handles.get("iteration")
        times_handle.wait_for_values(1)
        iteration_handle.wait_for_values(1)
        results = fetching_tool(job, data_list=["counts", "iteration"], mode="live")
        interrupt_on_close(fig, job)  # Interrupts the job when closing the figure
        while results.is_processing():
            counts, iteration = results.fetch_all()

            counts += prev_counts
            iteration += prev_iterations

            fig, ax = plot_rabi_live(t_vec, counts, lw=4, fig=fig, ax=ax,
                                     elapsed_iterations=iteration)
        job.halt()
        return counts, iteration


def pulsed_odmr(qmm, qm, fig, settings, prev_counts=0, prev_iterations=0, simulate=False, ax=None):
    """
    Pulsed ODMR Sequence
    :param qmm: Quantum Machines Manager Instance
    :param qm: Quantum Machine to perform measurement in.
    :param fig: Pyplot Figure handle to plot the live image in.
    :param settings: The specified measurement settings.
    :param prev_counts: The measured photon counts of the previous iteration.
    :param prev_iterations: The current iterations at the start of this measurement run.
    :param simulate: Simulation Flag.
    :param ax: Pyplot axis to plot in.
    :return: Current photon counts, current measurement iteration.
    """
    f_vec = settings['f_vec']  # +0.1 to include t_max in array
    n_avg = settings['n_avg']
    with program() as time_rabi:
        counts = declare(int)  # variable for number of counts
        counts_st = declare_stream()  # stream for counts
        times = declare(int, size=100)
        n = declare(int)  # variable to for_loop
        i = declare(int)  # variable to for_loop
        n_st = declare_stream()  # stream to save iterations
        test_counts = declare(int, size=len(f_vec))
        freq_vec = declare(int, value=[int(x) for x in f_vec])

        play("laser_ON", "AOM")
        wait(100, "AOM")
        with for_(n, 0, n < n_avg, n + 1):
            with for_(i, 0, i < test_counts.length(), i + 1):
                update_frequency('NV', freq_vec[i])
                play("const", "NV", duration=225 // 4)  # pulse of varied lengths
                align()
                play("laser_ON", "AOM")
                measure("readout", "APD", None, time_tagging.analog(times, meas_len, counts))
                assign(test_counts[i], counts + test_counts[i])
                save(test_counts[i], counts_st)  # save counts
                wait(100)
            save(n, n_st)  # save number of iteration inside for_loop

        with stream_processing():
            counts_st.buffer(len(f_vec)).save("counts")
            n_st.save("iteration")
    if simulate:
        simulation_config = SimulationConfig(duration=28000)
        job = qmm.simulate(config, time_rabi, simulation_config)
        job.get_simulated_samples().con1.plot()
        interrupt_on_close(fig, job)  # Interrupts the job when closing the figure
        return np.zeros(len(f_vec)), 0
    else:
        job = qm.execute(time_rabi)
        res_handles = job.result_handles
        times_handle = res_handles.get("counts")
        iteration_handle = res_handles.get("iteration")
        times_handle.wait_for_values(1)
        iteration_handle.wait_for_values(1)
        results = fetching_tool(job, data_list=["counts", "iteration"], mode="live")
        interrupt_on_close(fig, job)  # Interrupts the job when closing the figure
        while results.is_processing():
            counts, iteration = results.fetch_all()

            # Progress bar (Requires execution in console)
            progress_counter(iteration, n_avg, start_time=results.get_start_time())

            counts += prev_counts
            iteration += prev_iterations

            _, _ = plot_pulsed_odmr_live(f_vec, counts, lw=4, fig=fig, AX=ax,
                                         elapsed_iterations=iteration)
        job.halt()
        return counts, iteration


def ramsey(qmm, qm, fig, settings, frequency=None, prev_counts=0, prev_counts2=0, prev_iterations=0, simulate=False, ax=None):
    """

    :param qmm: Quantum Machines Manager Instance
    :param qm: Quantum Machine to perform measurement in.
    :param fig: Pyplot Figure handle to plot the live image in.
    :param settings: The specified measurement settings.
    :param prev_counts: The measured photon counts of the previous iteration.
    :param prev_counts2: The measured photons of the previous iteration after the frame rotation to a -pi/2 pulse.
    :param prev_iterations: The current iterations at the start of this measurement run.
    :param simulate: Simulation Flag.
    :param ax: Pyplot axis to plot in.
    :return: Current photon counts, current measurement iteration.
    """
    t_vec = settings['t_vec']  # +0.1 to include t_max in array
    n_avg = settings['n_avg']
    pi_half_time = 112.5
    if frequency is None:
        frequency=NV_IF_freq
    with program() as time_rabi:
        counts = declare(int)  # variable for number of counts
        counts_st = declare_stream()  # stream for counts

        counts2 = declare(int)  # variable for number of counts
        counts_2_st = declare_stream()  # stream for counts

        times = declare(int, size=100)
        times2 = declare(int, size=100)
        n = declare(int)  # variable to for_loop
        i = declare(int)  # variable to for_loop
        n_st = declare_stream()  # stream to save iterations
        test_counts = declare(int, size=len(t_vec))
        test_counts2 = declare(int, size=len(t_vec))
        times_vec = declare(int, value=[int(x) for x in t_vec])

        play("laser_ON", "AOM")
        wait(100, "AOM")
        update_frequency('NV', frequency)
        with for_(n, 0, n < n_avg, n + 1):
            with for_(i, 0, i < test_counts.length(), i + 1):
                play("const", "NV", duration=pi_half_time// 4)  # pulse of varied lengths
                align()
                wait(times_vec[i], 'NV')
                play("const", "NV", duration=pi_half_time // 4)  # pulse of varied lengths
                align()
                play("laser_ON", "AOM")
                measure("readout", "APD", None, time_tagging.analog(times, meas_len, counts))
                assign(test_counts[i], counts + test_counts[i])
                save(test_counts[i], counts_st)  # save counts

                align()

                play("const", "NV", duration=pi_half_time // 4)  # pulse of varied lengths
                wait(times_vec[i], "NV")  # variable delay in spin Echo
                frame_rotation_2pi(0.5, "NV")  # Turns next pulse to -x
                play("const", "NV", duration=pi_half_time // 4)  # pulse of varied lengths
                reset_frame("NV")
                align()
                play("laser_ON", "AOM")
                measure("readout", "APD", None, time_tagging.analog(times2, meas_len, counts2))
                assign(test_counts2[i], counts2 + test_counts2[i])
                save(test_counts2[i], counts_2_st)  # save counts
                wait(100)

            save(n, n_st)  # save number of iteration inside for_loop

        with stream_processing():
            counts_st.buffer(len(t_vec)).save("counts")
            counts_2_st.buffer(len(t_vec)).save("counts2")
            n_st.save("iteration")
    if simulate:
        simulation_config = SimulationConfig(duration=28000)
        job = qmm.simulate(config, time_rabi, simulation_config)
        job.get_simulated_samples().con1.plot()
        interrupt_on_close(fig, job)  # Interrupts the job when closing the figure
        return np.zeros(len(t_vec)), 0
    else:
        job = qm.execute(time_rabi)
        res_handles = job.result_handles
        times_handle = res_handles.get("counts")
        times2_handle = res_handles.get("counts2")
        iteration_handle = res_handles.get("iteration")
        times_handle.wait_for_values(1)
        times2_handle.wait_for_values(1)
        iteration_handle.wait_for_values(1)
        results = fetching_tool(job, data_list=["counts", "counts2", "iteration"], mode="live")
        interrupt_on_close(fig, job)  # Interrupts the job when closing the figure
        while results.is_processing():
            counts, counts2, iteration = results.fetch_all()

            # Progress bar (Requires execution in console)
            progress_counter(iteration, n_avg, start_time=results.get_start_time())
            counts += prev_counts
            counts2 += prev_counts2
            iteration += prev_iterations

            fig, ax = plot_ramsey_live(t_vec, counts, counts2, lw=4, fig=fig, ax=ax,
                                       elapsed_iterations=iteration)
        job.halt()
        return counts, counts2, iteration


def hahn(qmm, qm, fig, settings, prev_counts=0, prev_counts2=0, prev_iterations=0, simulate=False, ax=None):
    """

    :param qmm: Quantum Machines Manager Instance
    :param qm: Quantum Machine to perform measurement in.
    :param fig: Pyplot Figure handle to plot the live image in.
    :param settings: The specified measurement settings.
    :param prev_counts: The measured photon counts of the previous iteration.
    :param prev_counts2: The measured photons of the previous iteration after the frame rotation to a -pi/2 pulse.
    :param prev_iterations: The current iterations at the start of this measurement run.
    :param simulate: Simulation Flag.
    :param ax: Pyplot axis to plot in.
    :return: Current photon counts, current measurement iteration.
    """
    t_vec = settings['t_vec']  # +0.1 to include t_max in array
    n_avg = settings['n_avg']
    pi_time = 626
    with program() as time_rabi:
        counts = declare(int)  # variable for number of counts
        counts_st = declare_stream()  # stream for counts

        counts2 = declare(int)  # variable for number of counts
        counts_2_st = declare_stream()  # stream for counts

        times = declare(int, size=100)
        times2 = declare(int, size=100)
        n = declare(int)  # variable to for_loop
        i = declare(int)  # variable to for_loop
        n_st = declare_stream()  # stream to save iterations
        test_counts = declare(int, size=len(t_vec))
        test_counts2 = declare(int, size=len(t_vec))
        times_vec = declare(int, value=[int(x/2) for x in t_vec])

        play("laser_ON", "AOM")
        wait(100, "AOM")
        with for_(n, 0, n < n_avg, n + 1):
            with for_(i, 0, i < test_counts.length(), i + 1):
                play("const", "NV", duration=(pi_time/2) // 4)  # pulse of varied lengths
                align()
                wait(times_vec[i], 'NV')
                play("const", "NV", duration=(pi_time) // 4)  # pulse of varied lengths
                align()
                wait(times_vec[i], 'NV')
                play("const", "NV", duration=(pi_time/2)// 4)  # pulse of varied lengths
                align()
                play("laser_ON", "AOM")
                measure("readout", "APD", None, time_tagging.analog(times, meas_len, counts))
                assign(test_counts[i], counts + test_counts[i])
                save(test_counts[i], counts_st)  # save counts
                wait(500)

                align()

                play("const", "NV", duration=(pi_time/2) // 4)  # pulse of varied lengths
                align()
                wait(times_vec[i], 'NV')
                play("const", "NV", duration=(pi_time) // 4)  # pulse of varied lengths
                align()
                wait(times_vec[i], 'NV')
                frame_rotation_2pi(0.5, "NV")  # Turns next pulse to -x
                play("const", "NV", duration=(pi_time/2)// 4)  # pulse of varied lengths
                align()
                reset_frame("NV")
                align()
                play("laser_ON", "AOM")
                measure("readout", "APD", None, time_tagging.analog(times2, meas_len, counts2))
                assign(test_counts2[i], counts2 + test_counts2[i])
                save(test_counts2[i], counts_2_st)  # save counts
                wait(500, "AOM")

            save(n, n_st)  # save number of iteration inside for_loop

        with stream_processing():
            counts_st.buffer(len(t_vec)).save("counts")
            counts_2_st.buffer(len(t_vec)).save("counts2")
            n_st.save("iteration")
    if simulate:
        simulation_config = SimulationConfig(duration=28000)
        job = qmm.simulate(config, time_rabi, simulation_config)
        job.get_simulated_samples().con1.plot()
        interrupt_on_close(fig, job)  # Interrupts the job when closing the figure
        return np.zeros(len(t_vec)), 0
    else:
        job = qm.execute(time_rabi)
        res_handles = job.result_handles
        times_handle = res_handles.get("counts")
        times2_handle = res_handles.get("counts2")
        iteration_handle = res_handles.get("iteration")
        times_handle.wait_for_values(1)
        times2_handle.wait_for_values(1)
        iteration_handle.wait_for_values(1)
        results = fetching_tool(job, data_list=["counts", "counts2", "iteration"], mode="live")
        interrupt_on_close(fig, job)  # Interrupts the job when closing the figure
        while results.is_processing():
            counts, counts2, iteration = results.fetch_all()

            # Progress bar (Requires execution in console)
            progress_counter(iteration, n_avg, start_time=results.get_start_time())
            counts += prev_counts
            counts2 += prev_counts2
            iteration += prev_iterations

            fig, ax = plot_ramsey_live(t_vec, counts, counts2, lw=4, fig=fig, ax=ax,
                                       elapsed_iterations=iteration)
        job.halt()
        return counts, counts2, iteration


def ramsey_frequency_sweep(qmm, qm, fig, settings, pi_half_time, f=300000000, prev_counts=0, prev_counts2=0, prev_iterations=0, simulate=False, ax=None):
    """

    :param qmm: Quantum Machines Manager Instance
    :param qm: Quantum Machine to perform measurement in.
    :param fig: Pyplot Figure handle to plot the live image in.
    :param settings: The specified measurement settings.
    :param prev_counts: The measured photon counts of the previous iteration.
    :param prev_counts2: The measured photons of the previous iteration after the frame rotation to a -pi/2 pulse.
    :param prev_iterations: The current iterations at the start of this measurement run.
    :param simulate: Simulation Flag.
    :param ax: Pyplot axis to plot in.
    :return: Current photon counts, current measurement iteration.
    """
    t_vec = settings['t_vec']  # +0.1 to include t_max in array
    n_avg = settings['n_avg']
    with program() as time_rabi:
        counts = declare(int)  # variable for number of counts
        counts_st = declare_stream()  # stream for counts

        counts2 = declare(int)  # variable for number of counts
        counts_2_st = declare_stream()  # stream for counts

        times = declare(int, size=100)
        times2 = declare(int, size=100)
        n = declare(int)  # variable to for_loop
        i = declare(int)  # variable to for_loop
        freq = declare(int, value=f)
        n_st = declare_stream()  # stream to save iterations
        test_counts = declare(int, size=len(t_vec))
        test_counts2 = declare(int, size=len(t_vec))
        times_vec = declare(int, value=[int(x) for x in t_vec])

        play("laser_ON", "AOM")
        wait(100, "AOM")
        update_frequency('NV', freq)
        with for_(n, 0, n < n_avg, n + 1):
            with for_(i, 0, i < test_counts.length(), i + 1):
                play("const", "NV", duration=pi_half_time // 4)  # pulse of varied lengths
                align()
                wait(times_vec[i], 'NV')
                play("const", "NV", duration=pi_half_time // 4)  # pulse of varied lengths
                align()
                play("laser_ON", "AOM")
                measure("readout", "APD", None, time_tagging.analog(times, meas_len, counts))
                assign(test_counts[i], counts + test_counts[i])
                save(test_counts[i], counts_st)  # save counts
                wait(500)

                align()

                play("const", "NV", duration=pi_half_time  // 4)  # pulse of varied lengths
                wait(times_vec[i], "NV")  # variable delay in spin Echo
                frame_rotation_2pi(0.5, "NV")  # Turns next pulse to -x
                play("const", "NV", duration=pi_half_time // 4)  # pulse of varied lengths
                reset_frame("NV")
                align()
                play("laser_ON", "AOM")
                measure("readout", "APD", None, time_tagging.analog(times2, meas_len, counts2))
                assign(test_counts2[i], counts2 + test_counts2[i])
                save(test_counts2[i], counts_2_st)  # save counts
                wait(500, "AOM")

            save(n, n_st)  # save number of iteration inside for_loop

        with stream_processing():
            counts_st.buffer(len(t_vec)).save("counts")
            counts_2_st.buffer(len(t_vec)).save("counts2")
            n_st.save("iteration")
    if simulate:
        simulation_config = SimulationConfig(duration=28000)
        job = qmm.simulate(config, time_rabi, simulation_config)
        job.get_simulated_samples().con1.plot()
        interrupt_on_close(fig, job)  # Interrupts the job when closing the figure
        return np.zeros(len(t_vec)), 0
    else:
        job = qm.execute(time_rabi)
        res_handles = job.result_handles
        times_handle = res_handles.get("counts")
        times2_handle = res_handles.get("counts2")
        iteration_handle = res_handles.get("iteration")
        times_handle.wait_for_values(1)
        times2_handle.wait_for_values(1)
        iteration_handle.wait_for_values(1)
        results = fetching_tool(job, data_list=["counts", "counts2", "iteration"], mode="live")
        interrupt_on_close(fig, job)  # Interrupts the job when closing the figure
        while results.is_processing():
            counts, counts2, iteration = results.fetch_all()

            # Progress bar (Requires execution in console)
            progress_counter(iteration, n_avg, start_time=results.get_start_time())
            counts += prev_counts
            counts2 += prev_counts2
            iteration += prev_iterations

            fig, ax = plot_ramsey_live(t_vec, counts, counts2, lw=4, fig=fig, ax=ax,
                                       elapsed_iterations=iteration)
        job.halt()
        return counts, counts2, iteration

def refocus(qm, iteration=0, path='D:\\QM_OPX\\Data\\DATADUMP_DONT_USE'):
    """
    Dirty Jupyter Kernel hack to perform a QUDI optimizer run.
    :param qm: Quantum Machine to start the AOM.
    :param iteration: Current Optimizer iteration for file saving.
    :param path: Path to the save the optimizer snapshot to.
    """
    with program() as laser_ON:
        with infinite_loop_():
            play('laser_ON', 'AOM')
    timestamp = datetime.datetime.now().strftime("%y%m%d-%H%M%S")
    print('Laser ON for Refocus.')
    job_optim = qm.execute(laser_ON)
    command = 'optimizerlogic.start_refocus(scannerlogic.get_position(), "confocalgui")'
    print('Running Refocus.')
    run_kernel_command(cmd=command, wait=10)
    path = f'{os.path.join(path, f"refocus_{iteration}_{timestamp}.npz")}'.replace('\\', '\\\\')
    command2 = f'optimizerlogic.save_refocus_image("path={path}")'
    print(f'Saving Optimizer data to {path}.')
    run_kernel_command(cmd=command2, wait=2)
    print('Refocus done.')
    job_optim.halt()


def setup_qm():
    """
    Helper function to not crash other Quantum Machines. Checks for running jobs on the OPX and closes only jobs, that
    access the same ports as the to be executed script does.
    :return: Quantum Machines Manager, Quantum Machine Instance.
    """
    qmm = QuantumMachinesManager(host="192.168.1.254", port='80')
    for machine in qmm.list_open_quantum_machines():
        ports = qmm.get_qm(machine).get_config()['controllers']['con1']['digital_outputs']
        if 1 in ports:
            qmm.get_qm(machine).close()
    return qmm, qmm.open_qm(config, close_other_machines=False)


def EXPERIMENTAL_time_rabi_averaging(qmm, qm, fig, settings, frequency, amplitude=1,  prev_counts=0, prev_iterations=0, simulate=False,
                  ax=None):
    """
    EXPERIMENTAL Rabi measurement that compares averaging with summing.
    :param qmm: Quantum Machines Manager Instance
    :param qm: Quantum Machine to perform measurement in.
    :param fig: Pyplot Figure handle to plot the live image in.
    :param settings: The specified measurement settings.
    :param frequency: Frequency of the I-Q output for the microwave signal.
    :param amplitude: Amplitude of the microwave signal. (Only values between -2 and 2-2**-16 are valid).
    :param prev_counts: The measured photon counts of the previous iteration.
    :param prev_iterations: The current iterations at the start of this measurement run.
    :param simulate: Simulation Flag.
    :param ax: Pyplot axis to plot in.
    :return: Current photon counts, current measurement iteration.
    """
    t_vec = settings['t_vec']  # +0.1 to include t_max in array
    n_avg = settings['n_avg']
    with program() as time_rabi:
        counts = declare(int)  # variable for number of counts
        counts_st = declare_stream()  # stream for counts
        counts_avg_st = declare_stream()  # stream for counts
        times = declare(int, size=100)
        n = declare(int)  # variable to for_loop
        i = declare(int)  # variable to for_loop
        n_st = declare_stream()  # stream to save iterations
        test_counts = declare(int, size=len(t_vec))
        times_vec = declare(int, value=[int(x) for x in t_vec])

        play("laser_ON", "AOM")
        wait(100, "AOM")
        with for_(n, 0, n < n_avg, n + 1):
            with for_(i, 0, i < test_counts.length(), i + 1):
                update_frequency('NV', frequency)
                play("const" * amp(amplitude), "NV", duration=times_vec[i])  # pulse of varied lengths
                align()
                play("laser_ON", "AOM")
                measure("readout", "APD", None, time_tagging.analog(times, meas_len, counts))
                assign(test_counts[i], counts + test_counts[i])
                save(test_counts[i], counts_st)  # save counts
                save(counts, counts_avg_st)
                wait(100)
            save(n, n_st)  # save number of iteration inside for_loop

        with stream_processing():
            counts_st.buffer(len(t_vec)).save("counts")
            counts_avg_st.buffer(len(t_vec)).average().save("counts_avg")
            n_st.save("iteration")
    if simulate:
        simulation_config = SimulationConfig(duration=28000)
        job = qmm.simulate(config, time_rabi, simulation_config)
        job.get_simulated_samples().con1.plot()
        interrupt_on_close(fig, job)  # Interrupts the job when closing the figure
        return np.zeros(len(t_vec)), 0
    else:
        job = qm.execute(time_rabi)
        res_handles = job.result_handles
        times_handle = res_handles.get("counts")
        avg_handle = res_handles.get("counts")
        iteration_handle = res_handles.get("iteration")
        times_handle.wait_for_values(1)
        avg_handle.wait_for_values(1)
        iteration_handle.wait_for_values(1)
        results = fetching_tool(job, data_list=["counts", "counts_avg", "iteration"], mode="live")
        interrupt_on_close(fig, job)  # Interrupts the job when closing the figure
        while results.is_processing():
            counts, counts_avg, iteration = results.fetch_all()

            # Progress bar (Requires execution in console)
            progress_counter(iteration, n_avg, start_time=results.get_start_time())

            counts += prev_counts
            iteration += prev_iterations

            xlabel = r'Pulse Length $\tau$ [ns]'
            ylabel = 'Spin Contrast [arb. u.]'
            title = f'Time Rabi Iteration {iteration}'
            ax.scatter(np.array(t_vec)*4, counts / np.max(counts), linewidth=4)
            ax.scatter(np.array(t_vec)*4, counts_avg / np.max(counts_avg), marker='x', linewidth=4)
            for side in ax.spines.keys():
                ax.spines[side].set_linewidth(3)
            ax.yaxis.set_ticks(np.flip(np.arange(1, min(counts/ np.max(counts)) - 0.05, -0.05)))
            ax.tick_params(axis='x', direction='in', length=8, width=3)
            ax.tick_params(axis='y', direction='in', length=8, width=3)
            ax.set_title(title)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            plt.minorticks_on()
            ax.xaxis.set_minor_locator(AutoMinorLocator(2))
            ax.yaxis.set_minor_locator(AutoMinorLocator(2))
            plt.grid(which='major', linewidth=1)
            plt.grid(which='minor', linewidth=1, linestyle='--')
            plt.tight_layout()
            plt.pause(0.1)
            if type(ax) is tuple:
                ax[0].clear()
                ax[1].clear()
            else:
                ax.clear()
        job.halt()
        return counts, iteration

def EXPERIMENTAL_time_rabi_averaging_summing(qmm, qm, fig, prev_avg, settings, frequency, amplitude=1, simulate=False,
                                     ax=None):
    t_vec = settings['t_vec']  # +0.1 to include t_max in array
    n_avg = settings['n_avg']
    with program() as time_rabi:
        counts = declare(int)  # variable for number of counts
        counts_st = declare_stream()  # stream for counts
        times = declare(int, size=100)
        n = declare(int)  # variable to for_loop
        i = declare(int)  # variable to for_loop
        n_st = declare_stream()  # stream to save iterations
        test_counts = declare(float, value=prev_avg)
        times_vec = declare(int, value=[int(x) for x in t_vec])
        with for_(i, 0, i < test_counts.length(), i + 1):
            save(test_counts[i], counts_st)

        play("laser_ON", "AOM")
        wait(100, "AOM")
        with for_(n, 0, n < n_avg, n + 1):
            with for_(i, 0, i < test_counts.length(), i + 1):
                update_frequency('NV', frequency)
                play("const" * amp(amplitude), "NV", duration=times_vec[i])  # pulse of varied lengths
                align()
                play("laser_ON", "AOM")
                measure("readout", "APD", None, time_tagging.analog(times, meas_len, counts))
                save(counts, counts_st)
                wait(100)
            save(n, n_st)  # save number of iteration inside for_loop

        with stream_processing():
            counts_st.buffer(len(t_vec)).average().save("counts")
            n_st.save("iteration")
    if simulate:
        simulation_config = SimulationConfig(duration=28000)
        job = qmm.simulate(config, time_rabi, simulation_config)
        job.get_simulated_samples().con1.plot()
        interrupt_on_close(fig, job)  # Interrupts the job when closing the figure
        return np.zeros(len(t_vec)), 0
    else:
        job = qm.execute(time_rabi)
        res_handles = job.result_handles
        times_handle = res_handles.get("counts")
        iteration_handle = res_handles.get("iteration")
        times_handle.wait_for_values(1)
        iteration_handle.wait_for_values(1)
        results = fetching_tool(job, data_list=["counts", "iteration"], mode="live")
        interrupt_on_close(fig, job)  # Interrupts the job when closing the figure
        while results.is_processing():
            counts, iteration = results.fetch_all()

            # Progress bar (Requires execution in console)
            progress_counter(iteration, n_avg, start_time=results.get_start_time())

            xlabel = r'Pulse Length $\tau$ [ns]'
            ylabel = 'Spin Contrast [arb. u.]'
            title = f'Time Rabi Iteration {iteration}'
            ax.scatter(np.array(t_vec)*4, counts / np.max(counts), linewidth=4)
            for side in ax.spines.keys():
                ax.spines[side].set_linewidth(3)
            ax.yaxis.set_ticks(np.flip(np.arange(1, min(counts/ np.max(counts)) - 0.05, -0.05)))
            ax.tick_params(axis='x', direction='in', length=8, width=3)
            ax.tick_params(axis='y', direction='in', length=8, width=3)
            ax.set_title(title)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            plt.minorticks_on()
            ax.xaxis.set_minor_locator(AutoMinorLocator(2))
            ax.yaxis.set_minor_locator(AutoMinorLocator(2))
            plt.grid(which='major', linewidth=1)
            plt.grid(which='minor', linewidth=1, linestyle='--')
            plt.tight_layout()
            plt.pause(0.1)
            if type(ax) is tuple:
                ax[0].clear()
                ax[1].clear()
            else:
                ax.clear()
        job.halt()
        return counts, iteration

def modulo(a, b):
    return a - (a/b*b)

def time_rabi_averaged(qmm, qm, settings, frequency, work_dir, measurement_tag='MISSING_MEASUREMENT_TAG', measurement_ID=0, optimizer_iterations=0, amplitude=1, simulate=False):
    scheme = 'rabi_averaged'
    t_vec = settings['t_vec']  # +0.1 to include t_max in array
    n_avg = settings['n_avg']
    with program() as counter:
        with infinite_loop_():
            play('laser_ON', 'AOM', duration=int(3000 // 4))
    with program() as time_rabi:
        counts = declare(int)  # variable for number of counts
        counts_st = declare_stream()  # stream for counts
        times = declare(int, size=100)
        n = declare(int)  # variable to for_loop
        i = declare(int)  # variable to for_loop
        n_st = declare_stream()  # stream to save iterations
        test_counts = declare(int, size=len(t_vec))
        times_vec = declare(int, value=[int(x) for x in t_vec])

        play("laser_ON", "AOM")
        wait(100, "AOM")
        with if_(n_avg < 0):
            with infinite_loop_():
                assign(n, n+1)
                save(n, n_st)  # save number of iteration inside for_loop
                with if_(modulo(n, optimizer_iterations) == 0):
                    with for_(i, 0, i < 10000, i + 1):
                        play("laser_ON", "AOM", duration=1000000 // 4)
                    pause()
                with for_(i, 0, i < test_counts.length(), i + 1):
                    update_frequency('NV', frequency)
                    play("const" * amp(amplitude), "NV", duration=times_vec[i])  # pulse of varied lengths
                    align()
                    play("laser_ON", "AOM")
                    measure("readout", "APD", None, time_tagging.analog(times, meas_len, counts))
                    save(counts, counts_st)  # save counts
                    #                wait(50000//4) # pause for save buffer
                    wait(100)
        with else_():
            with for_(n, 1, n < n_avg, n + 1):
                save(n, n_st)  # save number of iteration inside for_loop
                with if_(modulo(n, optimizer_iterations) == 0):
                    with for_(i, 0, i<10000, i+1):
                        play("laser_ON", "AOM", duration=1000000 // 4)
                    pause()
                with for_(i, 0, i < test_counts.length(), i + 1):
                    update_frequency('NV', frequency)
                    play("const" * amp(amplitude), "NV", duration=times_vec[i])  # pulse of varied lengths
                    align()
                    play("laser_ON", "AOM")
                    measure("readout", "APD", None, time_tagging.analog(times, meas_len, counts))
                    save(counts, counts_st)  # save counts
    #                wait(50000//4) # pause for save buffer
                    wait(100)

        with stream_processing():
            counts_st.buffer(len(t_vec)).average().save("counts")
            n_st.save("iteration")
    if simulate:
        simulation_config = SimulationConfig(duration=28000)
        job = qmm.simulate(config, time_rabi, simulation_config)
        job.get_simulated_samples().con1.plot()
        fig, ax = plt.subplots(1, 1)
        interrupt_on_close(fig, job)  # Interrupts the job when closing the figure
        return np.zeros(len(t_vec)), 0
    else:
        job = qm.execute(time_rabi)
        res_handles = job.result_handles
        times_handle = res_handles.get("counts")
        iteration_handle = res_handles.get("iteration")
        times_handle.wait_for_values(1)
        iteration_handle.wait_for_values(1)
        results = fetching_tool(job, data_list=["counts", "iteration"], mode="live")
        fig, ax = plt.subplots(1, 1)
        interrupt_on_close(fig, job)  # Interrupts the job when closing the figure
        while results.is_processing():
            qm.set_io1_value(1)
            counts, iteration = results.fetch_all()
            print(f'Processing iteration {iteration}')
            if(iteration%optimizer_iterations == 0):
                print('Optimizer')
                save_data(work_dir, scheme, measurement_tag,
                          file_id=measurement_ID,
                          optimizer_iteration=int(iteration/optimizer_iterations),
                          times=settings['t_vec'],
                          counts=counts,
                          iterations=iteration)
                save_pdf(scheme, work_dir, measurement_tag, settings['t_vec'], counts,
                         file_id=measurement_ID,
                         optimizer_iteration=int(iteration/optimizer_iterations))
                refocus(qm, iteration=int(iteration/optimizer_iterations), path=work_dir)
                job.resume()

            # Progress bar (Requires execution in console)
            progress_counter(iteration, n_avg, start_time=results.get_start_time())

            fig, ax = plot_rabi_live(t_vec, counts, lw=4, fig=fig, ax=ax,
                                     elapsed_iterations=iteration)
        job.halt()
        return counts, iteration

def time_rabi_averaged_2_dim_buffer(qmm, qm, settings, frequency, work_dir, measurement_tag='MISSING_MEASUREMENT_TAG', measurement_ID=0, optimizer_iterations=0, amplitude=1, simulate=False):
    scheme = 'rabi_averaged'
    t_vec = settings['t_vec']  # +0.1 to include t_max in array
    n_avg = settings['n_avg']
    with program() as time_rabi:
        counts = declare(int)  # variable for number of counts
        counts_st = declare_stream()  # stream for counts
        times = declare(int, size=100)
        n = declare(int)  # variable to for_loop
        i = declare(int)  # variable to for_loop
        n_st = declare_stream()  # stream to save iterations
        test_counts = declare(int, size=len(t_vec))
        times_vec = declare(int, value=[int(x) for x in t_vec])
        a = Random()

        play("laser_ON", "AOM")
        wait(100, "AOM")
        with if_(n_avg < 0):
            with infinite_loop_():
                assign(n, n+1)
                save(n, n_st)  # save number of iteration inside for_loop
                #with if_(modulo(n, optimizer_iterations) == 0):
                #    with for_(i, 0, i < 10000, i + 1):
                #        play("laser_ON", "AOM", duration=1000000 // 4)
                #    pause()
                with for_(i, 0, i < len(t_vec), i + 1):
                    update_frequency('NV', frequency)
                    play("const" * amp(amplitude), "NV", duration=times_vec[i])  # pulse of varied lengths
                    align()
                    #play("laser_ON", "AOM")
                    measure("readout", "APD", None, time_tagging.analog(times, meas_len, counts))
                    assign(counts, a.rand_int(200))
                    save(i, counts_st)
                    save(counts, counts_st)  # save counts
                    wait(500000//4)
                    #wait(100)
        #with else_():
        #    with for_(n, 1, n < n_avg, n + 1):
        #        save(n, n_st)
        #        with if_(modulo(n, optimizer_iterations) == 0):
        #            with for_(i, 0, i<10000, i+1):
        #                play("laser_ON", "AOM", duration=1000000 // 4)
        #            pause()
        #        with for_(i, 0, i < test_counts.length(), i + 1):
        #            update_frequency('NV', frequency)
        #            play("const" * amp(amplitude), "NV", duration=times_vec[i])  # pulse of varied lengths
        #            align()
        #            play("laser_ON", "AOM")
        #            measure("readout", "APD", None, time_tagging.analog(times, meas_len, counts))
        #            save(counts, counts_st)  # save counts
        #            #                wait(50000//4) # pause for save buffer
        #            wait(100)

        with stream_processing():
            counts_st.buffer(2).buffer(len(t_vec)).average().save_all("counts")
            n_st.save("iteration")
    if simulate:
        simulation_config = SimulationConfig(duration=28000)
        job = qmm.simulate(config, time_rabi, simulation_config)
        job.get_simulated_samples().con1.plot()
        fig, ax = plt.subplots(1, 1)
        interrupt_on_close(fig, job)  # Interrupts the job when closing the figure
        return np.zeros(len(t_vec)), 0
    else:
        job = qm.execute(time_rabi)
        res_handles = job.result_handles
        times_handle = res_handles.get("counts")
        iteration_handle = res_handles.get("iteration")
        times_handle.wait_for_values(1)
        iteration_handle.wait_for_values(1)
        results = fetching_tool(job, data_list=["counts", "iteration"], mode="live")
        fig, ax = plt.subplots(1, 1)
        interrupt_on_close(fig, job)  # Interrupts the job when closing the figure
        while results.is_processing():
            res_counts, iteration = results.fetch_all()
            print(f'{iteration} : {res_counts}')
            print(f'Processing iteration {iteration}')
            #if(iteration%optimizer_iterations == 0):
            #    print('Optimizer')
            #    save_data(work_dir, scheme, measurement_tag,
            #              file_id=measurement_ID,
            #              optimizer_iteration=int(iteration/optimizer_iterations),
            #              times=settings['t_vec'],
            #              counts=res_counts,
            #              iterations=iteration)
            #    save_pdf(scheme, work_dir, measurement_tag, settings['t_vec'], res_counts,
            #             file_id=measurement_ID,
            #             optimizer_iteration=int(iteration/optimizer_iterations))
            #    refocus(qm, iteration=int(iteration/optimizer_iterations), path=work_dir)
            #    job.resume()

            #fig, ax = plot_rabi_live(t_vec, res_counts, lw=4, fig=fig, ax=ax,
            #                         elapsed_iterations=iteration)
        job.halt()
        return res_counts, iteration
