"""
A continuous wave optically detected magnetic resonance experiment sweeping the frequency of the microwave.
"""
from lib.sequences import *
from lib.data_handler import *


my_settings = {
    'f_min': 2.855e9,  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
    'f_max': 2.885e9,  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
    'df': 0.3e6,  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
    'n_avg': 100
}
my_settings.update({'f_vec': np.arange(my_settings['f_min'] - NV_LO_freq, my_settings['f_max'] - NV_LO_freq + 0.1,
                                       my_settings['df']).tolist()})

scheme = 'odmr'
measurement_tag = f'hochaufgeloestes_odmr'
work_dir = set_up_measurement(scheme, measurement_tag=measurement_tag, settings_file='measurement_settings',
                              settings=my_settings, LP=0.9)

qmm, qm = setup_qm()

counts = np.zeros(len(my_settings['f_vec']), dtype=np.int64)
simulate = False
fig, ax = plt.subplots(1, 1)
iteration = 0
i = 0
measurement_ID = generate_measurement_id(work_dir)
while 1:
    refocus(qm, iteration=i, path=work_dir)
    counts, iteration = cw_odmr(qmm, qm, fig, my_settings, counts, iteration, simulate=False, ax=ax)
    save_data(work_dir, scheme, measurement_tag, file_id=measurement_ID, optimizer_iteration=i, freq=my_settings['f_vec'],
              counts=counts, iterations=iteration)
    save_pdf(scheme, work_dir, measurement_tag, my_settings['f_vec'], counts, file_id=measurement_ID,
             optimizer_iteration=i)
    i += 1
