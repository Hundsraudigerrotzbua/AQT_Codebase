"""
A rabi experiment sweeping the time of the microwave pulse.
"""
from lib.sequences import *

my_settings = {
    't_min': 16,  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
    't_max': 3500,  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
    'dt': 150,  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
    'n_avg': -1,
    # Dauer bis Optimizer: len(np.arange(t_min, t_max, dt))*3.5e-6 * n_avg (3.5e-6 ist ungefähre Dauer für Laser + Warten)
    'Laser power (mW)': 0.9,
    'Laser power measured at': 'Infront of dichroic mirror',
    'emission_filter': 'BasicEdge',
}
my_settings.update(
    {'t_vec': np.arange(my_settings['t_min'] // 4, my_settings['t_max'] // 4 + 0.1, my_settings['dt'] // 4).tolist()})

scheme = 'rabi'
measurement_tag = f'check_if_buffer_averaging_jumps_too'
work_dir = set_up_measurement(scheme, measurement_tag=measurement_tag, settings_file='measurement_settings',
                              settings=my_settings)

measurement_ID = generate_measurement_id(work_dir)
qmm, qm = setup_qm()
simulate = False
counts = np.zeros(len(my_settings['t_vec']), dtype=np.int64)
iteration = 0
while 1:
    counts, iteration = time_rabi_averaged_2_dim_buffer(qmm, qm,
                                           frequency=301.25e6,
                                           settings=my_settings,
                                           optimizer_iterations=2e6,
                                           work_dir=work_dir,
                                           measurement_tag=measurement_tag,
                                           measurement_ID=measurement_ID,
                                           )
qm.close()
