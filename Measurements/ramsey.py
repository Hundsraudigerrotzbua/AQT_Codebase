"""
A Ramsey experiment sweeping the duration of the Dephasing Time.
"""
from lib.sequences import *
from lib.data_handler import *

my_settings = {
    't_min': 16,  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
    't_max': 800,  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
    'dt': 40,  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
    'n_avg': 1.5e6,
    'Laser power (mW)': 0.6,
    'Laser power measured at': 'Infront of dichroic mirror',
    'emission_filter': 'BasicEdge',
}
my_settings.update({'t_vec': np.arange(my_settings['t_min']//4, my_settings['t_max']//4 + 0.1, my_settings['dt']//4).tolist()})

scheme = 'ramsey'
file_tag = 'ramsey_frequency_sweep'
work_dir = set_up_measurement(scheme, measurement_tag=file_tag, settings_file='hardwarefile',
                              settings=my_settings, script_path=os.path.realpath(__file__))
qmm, qm = setup_qm()

simulate = False
counts = np.zeros(len(my_settings['t_vec']), dtype=np.int64)
counts2 = np.zeros(len(my_settings['t_vec']), dtype=np.int64)
iteration = 0
fig, ax = plt.subplots(1, 1)
i = 0
NV_IF_freq_array = np.arange(295e6, 305e6, 0.5e6)
for f in NV_IF_freq_array:
    file_tag = file_tag + f'_f{str(f*1e-6).replace(".", ",")}MHz'
    i=0
    measurement_ID = generate_measurement_id(work_dir)
    for _ in range(0, 2):
        refocus(qm, iteration=i, path=work_dir)
        counts, counts2, iteration = ramsey(qmm, qm, fig,
                                            frequency=f,
                                            settings=my_settings,
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
qm.close()
