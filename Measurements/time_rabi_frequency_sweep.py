"""
A rabi experiment sweeping the time of the microwave pulse as well as the frequency and the amplitude of said pulse.
"""
from lib.sequences import *
from lib.data_handler import *
from lib.misc_lib import dbm_to_vp

my_settings = {
    't_min': 16,  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
    't_max': 3000,  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
    'dt': 50,  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
    'n_avg': 1.2e6
}
my_settings.update(
    {'t_vec': np.arange(my_settings['t_min'] // 4, my_settings['t_max'] // 4 + 0.1, my_settings['dt'] // 4).tolist()})

qmm, qm = setup_qm()
simulate = False

scheme = 'rabi_sweep'
measurement_tag = f'Rabi_Time-Power_Graph'
work_dir = set_up_measurement(scheme, measurement_tag=measurement_tag, settings_file='measurement_settings',
                              settings=my_settings, LP=0.9)

### AMPLITUDE ###
amp_array = dbm_to_vp(np.linspace(-27, -6, 8))/mw_amp_NV
amp_array = [x for x in amp_array if x < 2-2**-16] # the amp(x) value can't exceed 2-2**-16 (QM Documentation)

### FREQUENCY ###
df = 0.5e6  # Frequency step size
bw = 2e6  # Bandwidth to sweep over
freq_array = np.concatenate(
    (np.arange(300e6 - bw // 2, NV_IF_freq, df), np.arange(NV_IF_freq, NV_IF_freq + bw // 2 + 0.1, df)))

freq_array = [300e6] # Overwrite frequency for single point.

fig, ax = plt.subplots(1, 1)
i = 0
for a in amp_array:
    for f in freq_array:
        measurement_ID = generate_measurement_id(work_dir)
        print(f'Starting Iteration for f={f + NV_LO_freq} / a={a * mw_amp_NV}.')
        counts = np.zeros(len(my_settings['t_vec']), dtype=np.int64)
        iteration = 0
        for i in range(0, 4):
            refocus(qm, iteration=i, path=work_dir)
            counts, iteration = time_rabi(qmm, qm, fig, my_settings, a, f,
                                                prev_counts=counts, prev_iterations=iteration, ax=ax)
            save_data(work_dir, scheme,f'{measurement_tag}_f{f + NV_LO_freq}_a{a * mw_amp_NV}', file_id=measurement_ID,
                      optimizer_iteration=i,
                      times=my_settings['t_vec'], counts=counts, iterations=iteration)
            save_pdf(scheme, work_dir, f'{measurement_tag}_f{f + NV_LO_freq}_a{a * mw_amp_NV}', my_settings['t_vec'],
                     counts, file_id=measurement_ID, optimizer_iteration=i)
qm.close()
