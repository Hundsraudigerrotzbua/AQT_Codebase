"""
A pulsed ODMR experiment sweeping the frequency of the applied pulse.
"""
from lib.data_handler import *
from lib.sequences import *
import matplotlib
matplotlib.use('Qt5Agg')

#########################
###                   ###
###    Pulsed ODMR    ###
###                   ###
#########################

qmm, qm = setup_qm()

my_settings = {
    'f_min': 2.855e9,  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
    'f_max': 2.885e9,  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
    'df': 1e6,  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
    'n_avg': 2000000
}
my_settings.update({'f_vec': np.arange(my_settings['f_min'] - NV_LO_freq, my_settings['f_max'] - NV_LO_freq + 0.1,
                                       my_settings['df']).tolist()})

scheme = 'pulsed_odmr'
measurement_tag = f'pulsed_odmr_to_determine_resonance_frequency'
work_dir = set_up_measurement(scheme, measurement_tag=measurement_tag, settings_file='hardwarefile',
                              settings=my_settings, script_path=__file__)

simulate = False
counts = np.zeros(len(my_settings['f_vec']), dtype=np.int64)
fig, ax = plt.subplots(1, 1)
measurement_ID = generate_measurement_id(work_dir)
iteration = 0
i = 0
while 1:
    refocus(qm, iteration=i, path=work_dir)
    counts, iteration = pulsed_odmr(qmm, qm, fig, my_settings, counts, iteration, simulate=False, ax=ax)
    save_data(work_dir, scheme, measurement_tag, file_id=measurement_ID, optimizer_iteration=i, freq=my_settings['f_vec'],
              counts=counts, iterations=iteration)
    save_pdf(scheme, work_dir, measurement_tag, my_settings['f_vec'], counts, file_id=measurement_ID,
             optimizer_iteration=i)
    i += 1
