import matplotlib.pyplot as plt
from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
from configuration_widefield import *
from qm import SimulationConfig
import datetime
from Playground.trigger_and_sweep_windfreak import OPX_MW
from qualang_tools.results import progress_counter, fetching_tool
import ctypes

import ctypes
import numpy as np
from configuration_widefield import cm_exposure_time, cm_EM_Gain

def start_MW(MW_freq, MW_pwr):
    MW = OPX_MW()
    MW.activate()
    print('MW Settings:')
    print(MW.set_cw(frequency=MW_freq, power=MW_pwr))  # MW settings for the IQ mixer
    print('Power up LO...')
    MW.cw_on()
    return MW

def end_MW(MW):
    print('Shutting down MW...')
    MW.off()
    print('Deactivating MW...')
    MW.deactivate()


def capture(frames_per_window, frequency):
    print(f'Beginning ODMR with N={frames_per_window} - f={frequency}')
    with program() as wf_odmr:
        frame_st = declare_stream()
        n = declare(int)
        f = declare(int)
        f_vec = declare(int, value=[int(x) for x in frequency])
        wait_for_trigger('camera')
        with for_(f, 0, f < f_vec.length(), f + 1):
            update_frequency('NV', f_vec[f])
            play('const', 'NV')
            wait(int(t_puffer) // 4, 'camera')
            with for_(n, (f * 2) * frames_per_window, n < (f * 2 + 1) * frames_per_window, n + 1):
                play('camera_trigger_ON', 'camera')
                save(n, frame_st)
                wait_for_trigger('camera')
            align()
            play('const'*amp(-1), 'NV')
            wait(int(t_puffer)//4, 'camera')
            with for_(n, (f * 2 + 1) * frames_per_window, n < (f * 2 + 2) * frames_per_window, n + 1):
                play('camera_trigger_ON', 'camera')
                save(n, frame_st)
                with if_(n+1 < frames_per_window * 2 * f_vec.length()):
                    wait_for_trigger('camera')

        with stream_processing():
            frame_st.save('frame')

    simulate = 0
    if simulate:
        simulation_config = SimulationConfig(duration=12000)
        job = qmm.simulate(config, wf_odmr, simulation_config)
        job.get_simulated_samples().con1.plot()
        plt.show()
    else:
        job = qm.execute(wf_odmr)  # execute QUA program
        print(job.execution_report())
    #results = fetching_tool(job, data_list=["frame"], mode="live")
    return job
    #return results, job

# Camera settings
# buffer time to allow MW signal to be fully established
t_puffer = 100e-6 * 1e9
# exposure time for the shutter
t_exposure = cm_exposure_time * 1e-3 * 1e9
# time for the image readout and cleaning
t_readout_and_cleaning = cm_readout_cleaning_time * 1e-3 * 1e9

cm_frames_per_window = 1500
mw_amp_NV = 0.2  # in units of volts
mw_amp = np.arange(0.05, 0.25+0.01, 0.05)

#f_vec_array = np.array([2.68, 2.77, 2.87, 2.97, 3.07])*1e9
#f = np.array([2.68, 2.77, 2.87, 2.97, 3.07])*1e9
f = np.arange(2.67e9, 3.07e9, 40e6)
iteration_array = [f[i:i+3] for i in np.arange(0, len(f), 3)]

for idx1, mw_amp_NV in enumerate(mw_amp):
    for idx2, f_vec_array in enumerate(iteration_array):
        cm_total_frames = str(cm_frames_per_window * 2 * len(f_vec_array)) # ms
        f_vec_OPX = f_vec_array - NV_LO_freq
        cm_file_name = f'D:\\Widefield\\Daten\\telescope_max_focus\\detailed_ODMR_sweep_try1_mw-{idx1}_f-{idx2}.raw'
        loaded_config = create_config(mw_amp_NV)
        qmm = QuantumMachinesManager(host="192.168.1.254", port='80')
        qm = qmm.open_qm(loaded_config, close_other_machines=False)


        begin = datetime.datetime.now()
        print(
            f'Starting {begin.strftime("%d.%m.%y - %H:%M:%S")} - {cm_frames_per_window} frames per frequency...')
        MW = start_MW(NV_LO_freq, NV_LO_pwr)
        print('Starting run...')
        #results, job = capture(cm_frames_per_window, f_vec_OPX)
        job = capture(cm_frames_per_window, f_vec_OPX)
        print('Started OPX...')
        path_to_lib = 'D:\\Widefield\\Code\\PICAM_Code\\test_compile3.so'
        lib = ctypes.cdll.LoadLibrary(path_to_lib)
        lib.main.restype = ctypes.c_int
        lib.main.argtypes = ctypes.c_int, ctypes.POINTER(ctypes.c_char_p)
        args = (ctypes.c_char_p * 4)(str(cm_total_frames).encode(), str(cm_exposure_time).encode(), str(cm_EM_Gain).encode(), cm_file_name.encode())

        print('Starting Camera...')
        print(lib.main(len(args), args))

        print('Finished run.')
        end_MW(MW)
        end = datetime.datetime.now()
        print(f'Finished at {end}.')
        print(f'Elapsed time: {end - begin}.')

        print(f'\nClosing down OPX...')
        if job.halt() and qm.close():
            print(f'Successfully closed OPX job.')
        else:
            raise ConnectionRefusedError('Error when closing down OPX.')


#sourceFile = open('widefield_odmr.py', 'w')
#print(generate_qua_script(wf_odmr, config), file=sourceFile)
#sourceFile.close()
