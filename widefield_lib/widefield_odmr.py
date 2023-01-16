import matplotlib.pyplot as plt
from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
from qm import generate_qua_script
from configuration_widefield import *
from qm import SimulationConfig
import datetime
from Playground.trigger_and_sweep_windfreak import OPX_MW
from qualang_tools.results import progress_counter, fetching_tool
import ctypes

qmm = QuantumMachinesManager(host="192.168.1.254", port='80')
qm = qmm.open_qm(config, close_other_machines=False)

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
        with for_(f, 0, f < f_vec.length(), f + 1):
            update_frequency('NV', f_vec[f])
            play('const', 'NV')
            wait(int(t_puffer) // 4, 'camera')
            with for_(n, (f * 2) * frames_per_window, n < (f * 2 + 1) * frames_per_window, n + 1):
                play('camera_trigger_ON', 'camera')
                wait(int(t_exposure + t_readout_and_cleaning) // 4, 'camera')
                save(n, frame_st)
            align()
            play('const'*amp(-1), 'NV')
            wait(int(t_puffer)//4, 'camera')
            with for_(n, (f * 2 + 1) * frames_per_window, n < (f * 2 + 2) * frames_per_window, n + 1):
                play('camera_trigger_ON', 'camera')
                wait(int(t_exposure + t_readout_and_cleaning) // 4, 'camera')
                save(n, frame_st)


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
    results = fetching_tool(job, data_list=["frame"], mode="live")
    return results, job

# Camera settings
# buffer time to allow MW signal to be fully established
t_puffer = 100e-6 * 1e9
# exposure time for the shutter
t_exposure = cm_exposure_time * 1e-3 * 1e9
# time for the image readout and cleaning
t_readout_and_cleaning = cm_readout_cleaning_time * 1e-3 * 1e9

# convert to OPX values for IQ mixing
f_vec_OPX = f_vec_array - NV_LO_freq
# frames per frequency window (multiplied by two because of ref img)
n_frames_per_window = cm_frames_per_window
# calculate number of frames DEPRECATED !

begin = datetime.datetime.now()
print(
    f'Starting {begin.strftime("%d.%m.%y - %H:%M:%S")} - {n_frames_per_window} frames per frequency...')
MW = start_MW(NV_LO_freq, NV_LO_pwr)
print('Starting run...')
results, job = capture(n_frames_per_window, f_vec_OPX)
while results.is_processing():
    frame = results.fetch_all()[0] + 1
    now = datetime.datetime.now()
    elapsed_time = (now-begin).total_seconds()
    fps = frame / elapsed_time
    ETA = datetime.timedelta(seconds=2 * n_frames_per_window * len(f_vec_array) / fps - elapsed_time)
    print(
        f"[%-50s] %d%% - %d/%d Frames captued. ETA: {ETA}" % ('=' * int(50 * frame / (2 * n_frames_per_window * len(f_vec_array))),
                                                  100 * frame / (2 * n_frames_per_window * len(f_vec_array)), frame,
                                                  (2 * n_frames_per_window * len(f_vec_array))), end='\r', flush=True)

print("[%-50s] %d%% - %d/%d Frames captued." % ('=' * int(50 * frame / (2 * n_frames_per_window * len(f_vec_array))),
                                                100 * frame / (2 * n_frames_per_window * len(f_vec_array)), frame,
                                                (2 * n_frames_per_window * len(f_vec_array))))
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
