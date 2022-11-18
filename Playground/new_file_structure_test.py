from lib.data_handler import *

work_dir = set_up_measurement('odmr', measurement_tag='test_messung', settings_file='testfile_OHNE_PYTHON_CODE',
                       settings={'test': 'test123'}, LP=0.9, emission_filter='BasicEdge', script_path=os.path.realpath(__file__))

for iteration in range(0, 3):
    measurement_ID = generate_measurement_id(work_dir)
    for optim in range(0, 10):
        save_data(work_dir, scheme='ramsey', filetag=f'{iteration}_this_is_a_test', file_id=measurement_ID,
                  optimizer_iteration=optim,
                  test=[1, 2, 3, 4])
