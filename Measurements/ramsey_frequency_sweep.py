"""
A Ramsey experiment sweeping the duration of the Dephasing Time.
"""
from lib.sequences import *
from lib.data_handler import *

freq_array = np.arange(2.867e9 - 2.57e9, 2.873e9-2.57e9, 0.5e6)
freq_array = [2.871e9-2.57e9 - 15e6, 2.871e9-2.57e9]
for f in freq_array:
    my_settings = {
        't_min': 16,  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
        't_max': 300,  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
        'dt': 20,  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
        'n_avg': 3.5e6,
        'Laser power (mW)': 0.62,
        'Laser power measured at': 'Infront of dichroic mirror',
        'emission_filter': 'BasicEdge',
    }
    my_settings.update({'t_vec': np.arange(my_settings['t_min']//4, my_settings['t_max']//4 + 0.1, my_settings['dt']//4).tolist()})

    scheme = 'ramsey'
    file_tag = f'ramsey_sweep_at{np.round(f*1e-6, 1)}_MHz'
    work_dir = set_up_measurement(scheme, measurement_tag=file_tag, settings_file='hardwarefile',
                                  settings=my_settings, script_path=os.path.realpath(__file__))
    qmm, qm = setup_qm()

    simulate = False
    counts = np.zeros(len(my_settings['t_vec']), dtype=np.int64)
    counts2 = np.zeros(len(my_settings['t_vec']), dtype=np.int64)
    iteration = 0
    fig, ax = plt.subplots(1, 1)
    i = 0
    measurement_ID = generate_measurement_id(work_dir)
    for _ in range(40):
        refocus(qm, iteration=i, path=work_dir)
        counts, counts2, iteration = ramsey_frequency_sweep(qmm, qm, fig,
                                                            settings=my_settings,
                                                            pi_half_time=696,
                                                            f=int(f),
                                                            prev_counts=counts,
                                                            prev_counts2=counts2,
                                                            prev_iterations=iteration,
                                                            ax=ax)
        save_data(work_dir, scheme, file_tag,
                  file_id=measurement_ID,
                  optimizer_iteration=i,
                  times=my_settings['t_vec'],
                  counts=counts,
                  counts2=counts2,
                  iterations=iteration,
                  )
        save_pdf(scheme, work_dir, file_tag, my_settings['t_vec'], counts, alternate_y=counts2, file_id=measurement_ID, optimizer_iteration=i)
        i += 1
    fig.close()
    qm.close()
