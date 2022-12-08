"""
A rabi experiment sweeping the time of the microwave pulse.
"""
from lib.sequences import *
from lib.data_handler import *

my_settings = {
    't_min': 16,  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
    't_max': 3500,  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
    'dt': 150,  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
    'n_avg': 2.5e6,
    # Dauer bis Optimizer: len(np.arange(t_min, t_max, dt))*3.5e-6 * n_avg (3.5e-6 ist ungefähre Dauer für Laser + Warten)
    'Laser power (mW)': 0.9,
    'Laser power measured at': 'Infront of dichroic mirror',
    'emission_filter': 'BasicEdge',
}
my_settings.update(
    {'t_vec': np.arange(my_settings['t_min'] // 4, my_settings['t_max'] // 4 + 0.1, my_settings['dt'] // 4).tolist()})

scheme = 'rabi'
measurement_tag = f'rabi_comparing_averaging_vs_summing'
work_dir = set_up_measurement('rabi', measurement_tag=measurement_tag, settings_file='measurement_settings',
                              settings=my_settings)

measurement_ID = generate_measurement_id(work_dir)
qmm, qm = setup_qm()
simulate = False
counts = np.zeros(len(my_settings['t_vec']), dtype=np.int64)
fig, ax = plt.subplots(1, 1)
iteration = 0
i = 0
while 1:
    refocus(qm, iteration=i, path=work_dir)
    counts, iteration = EXPERIMENTAL_time_rabi_averaging(qmm, qm, fig,
                                                         frequency=300e6,
                                                         settings=my_settings,
                                                         prev_counts=counts,
                                                         prev_iterations=iteration,
                                                         ax=ax)
    save_data(work_dir, scheme, measurement_tag,
              file_id=measurement_ID,
              optimizer_iteration=i,
              times=my_settings['t_vec'],
              counts=counts,
              iterations=iteration)
    save_pdf(scheme, work_dir, measurement_tag, my_settings['t_vec'], counts, file_id=measurement_ID,
             optimizer_iteration=i)
    i += 1
# execute QUA program
qm.close()
