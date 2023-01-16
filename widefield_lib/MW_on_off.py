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


with program() as wf_odmr:
    frame_st = declare_stream()
    with infinite_loop_():
        play('const', 'NV')
        save(1, frame_st)
        wait(int(3e9) // 4)
        play('const'*amp(-1), 'NV')
        save(3, frame_st)
        wait(int(3e9) // 4)

    with stream_processing():
        frame_st.save('frame')

MW = start_MW(NV_LO_freq, NV_LO_pwr)
print('Starting run...')
job = qm.execute(wf_odmr)  # execute QUA program
print(job.execution_report())
results = fetching_tool(job, data_list=["frame"], mode="live")
while results.is_processing():
    frame = results.fetch_all()[0]
    print(f'{frame}')
end_MW(MW)
end = datetime.datetime.now()
print(f'Finished.')
