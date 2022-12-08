import datetime
import json
from lib.plot_lib import *

data_path = 'Z:\\quantech\\DATA'
config_path = 'D:\\QM_OPX\\configuration.py'
library_path = 'D:\\QM_OPX\\lib'


def set_up_measurement(scheme, measurement_tag=None, settings_file=None, settings={'None': None}, script_path=None):
    """
    Create a unique measurement data structure for the corresponding scheme.
    :param scheme: (str) Name of the scheme to be measured.
    :param measurement_tag: (str) String to identify measurement with.
    :param settings_file: (str) Name of the hardware file to be created. This contains the hardware parameters as well as the OPX configuration.
    :param settings: (dict) Dictionary containing all required measurement settings.
    :return: (str) Path of the created experiment directory.
    """
    month = str(datetime.datetime.now().month)
    year = str(datetime.datetime.now().year)
    daystamp = datetime.datetime.now().strftime("%Y%m%d")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H-%M-%S")
    if not os.path.exists(os.path.join(data_path, year)):
        os.mkdir(os.path.join(data_path, year))
    if not os.path.exists(os.path.join(data_path, year, month)):
        os.mkdir(os.path.join(data_path, year, month))
    if not os.path.exists(os.path.join(data_path, year, month, daystamp)):
        os.mkdir(os.path.join(data_path, year, month, daystamp))

    dirs = next(os.walk(os.path.join(data_path, year, month, daystamp)))[1]
    dirs = [x for x in dirs if x.split('_')[0].isdigit()]
    dirs.sort(key=lambda x: int(x.split('_')[0]))
    if len(dirs) == 0:
        meas_id = 1
    else:
        meas_id = int(dirs[-1].split('_')[0]) + 1
    if measurement_tag is not None:
        measurement = f'{meas_id}_{timestamp}_{scheme}__{measurement_tag}'
    else:
        measurement = f'{meas_id}_{timestamp}_{scheme}'
    final_path = os.path.join(data_path, year, month, daystamp, measurement)
    os.mkdir(final_path)

    if settings_file is not None:
        with open(config_path, 'r') as f:
            # config_file = [line.rstrip() for line in f]
            config_file = f.read()
        with open(os.path.join(library_path, 'sequences.py'), 'r')  as f:
            sequence_file = f.read()
    if script_path is not None:
        with open(os.path.join(script_path), 'r') as f:
            script_file = f.read()
    else:
        script_file = None

    hardware_settings = {
        'Measurement Settings': settings,
        'OPX Config': config_file,
        'Sequence File': sequence_file,
        'Measurement Script': script_file,
    }
    with open(os.path.join(final_path, f'{settings_file}.json'), 'w+') as f:
        json.dump(hardware_settings, f)

    return final_path


def save_data(measurement_path, scheme, filetag, *args, file_id=None, optimizer_iteration=0, **kwargs):
    """
    Wrapper function to properly save all measurements according to regulations.
    :param measurement_path: (str) Path to the experiment directory.
    :param scheme: (str) Scheme to be saved.
    :param filetag: (str) Experiment Identifier Tag.
    :param args: A number of instances can be handed as arguments and will be saved under the ['arr_X'] syntax of np.savez.
    :param file_id: (str) The file_ID to save the data under - will be generated automatically if left out.
    :param optimizer_iteration: (int) Optimizer Iteration.
    :param kwargs: A number of keyword arguments containing instances to be saved under a specified name.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H-%M-%S")
    if file_id is None:
        file_id = generate_measurement_id(measurement_path)
    file_tag = f'{file_id}_{optimizer_iteration}_{timestamp}_{scheme}__{filetag}.npz'
    np.savez(os.path.join(measurement_path, file_tag), *args, **kwargs)


def save_pdf(scheme, measurement_path, filename, x, y, alternate_y=np.array([]), file_id=None, optimizer_iteration=0):
    """
    Function to save measurement data as two PDfs.
    :param scheme: (str) The measured scheme.
    :param measurement_path: (str) Path to the measurement directory.
    :param filename: (str) Name tag of the measurement to be saved.
    :param x: (np.ndarray) x-data to be plotted.
    :param y: (np.ndarray) y-data to be plotted.
    :param alternate_y: (np.ndarray) Second y-array to be plotted (e.g. for Ramsey)
    :param file_id: (str) Unique file_ID
    :param optimizer_iteration: (str) Iterations of the optimizer in this measurement run.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H-%M-%S")
    file_tag_pdf = f'{file_id}_{optimizer_iteration}_{timestamp}_{scheme}__{filename}.pdf'
    file_tag_fit_pdf = f'{file_id}_{optimizer_iteration}_{timestamp}_{scheme}__{filename}_fit.pdf'
    file_tag_png = f'{file_id}_{optimizer_iteration}_{timestamp}_{scheme}__{filename}.png'
    file_tag_fit_png = f'{file_id}_{optimizer_iteration}_{timestamp}_{scheme}__{filename}_fit.png'
    if scheme.lower() == 'odmr':
        fig, ax = plot_odmr(x, y, lw=4, no_save=0, save=os.path.join(measurement_path, file_tag_pdf), fit=0)
        plt.close(fig)
        fig, ax = plot_odmr(x, y, lw=4, no_save=0, save=os.path.join(measurement_path, file_tag_fit_pdf), fit=1)
        plt.close(fig)
        fig, ax = plot_odmr(x, y, lw=4, no_save=0, save=os.path.join(measurement_path, file_tag_png), fit=0)
        plt.close(fig)
        fig, ax = plot_odmr(x, y, lw=4, no_save=0, save=os.path.join(measurement_path, file_tag_fit_png), fit=1)
        plt.close(fig)
    elif scheme.lower() == 'pulsed_odmr':
        fig, ax = plot_pulsed_odmr(x, y, lw=4, no_save=0, save=os.path.join(measurement_path, file_tag_pdf), fit=0)
        plt.close(fig)
        fig, ax = plot_pulsed_odmr(x, y, lw=4, no_save=0, save=os.path.join(measurement_path, file_tag_fit_pdf), fit=1)
        plt.close(fig)
        fig, ax = plot_pulsed_odmr(x, y, lw=4, no_save=0, save=os.path.join(measurement_path, file_tag_png), fit=0)
        plt.close(fig)
        fig, ax = plot_pulsed_odmr(x, y, lw=4, no_save=0, save=os.path.join(measurement_path, file_tag_fit_png), fit=1)
        plt.close(fig)
    elif scheme.lower() == 'rabi':
        fig, ax = plot_rabi(x, y, lw=4, no_save=0, save=os.path.join(measurement_path, file_tag_pdf), fit=0)
        plt.close(fig)
        fig, ax = plot_rabi(x, y, lw=4, no_save=0, save=os.path.join(measurement_path, file_tag_pdf), fit=1)
        plt.close(fig)
        fig, ax = plot_rabi(x, y, lw=4, no_save=0, save=os.path.join(measurement_path, file_tag_png), fit=0)
        plt.close(fig)
        fig, ax = plot_rabi(x, y, lw=4, no_save=0, save=os.path.join(measurement_path, file_tag_png), fit=1)
        plt.close(fig)
    elif scheme.lower() == 'ramsey':
        fig, ax = plot_ramsey(x, y, alternate_y, lw=4, no_save=0, save=os.path.join(measurement_path, file_tag_pdf), fit=0)
        plt.close(fig)
        fig, ax = plot_ramsey(x, y, alternate_y, lw=4, no_save=0, save=os.path.join(measurement_path, file_tag_png), fit=0)
        plt.close(fig)


def generate_measurement_id(measurement_path):
    """
    Automatically generate a ID for each measurement run.
    :param measurement_path: (str) Path to the experiment directory.
    :return: (int) File ID
    """
    files = os.listdir(measurement_path)
    files = [x for x in files if ('.npz' in x) and (x.split('_')[0].isdigit())]
    if len(files) == 0:
        file_id = '0'
    else:
        files.sort(key=lambda x: int(x.split('_')[0]))
        file_id = int(files[-1].split('_')[0]) + 1
    return file_id


def path_grabber(daystamp, scheme, file_id):
    """
    Helper function to navigate through the data structure easily.
    :param daystamp: (str) Day stamp of the experiment run to grab.
    :param scheme: (str) Scheme of the experiment run to grab.
    :param file_id: (str) Experiment ID of the experiment run to grab.
    :return: (list) List of strings containing all paths to the specified experiments.
    """
    year = daystamp[0:4]
    month = daystamp[4:6]
    scheme_path = os.path.join(data_path, year, month, daystamp)
    measurements = os.listdir(scheme_path)
    return [os.path.join(scheme_path, x) for x in measurements if f'{file_id}_{daystamp}' in x]


def file_grabber(measurement_path, meas_id=None, optim_id=None):
    """
    Helper function to grab measurement data from a provided experiment directory.
    :param measurement_path: (str) Path to the experiment directory to grab data from.
    :param meas_id: (str) Measurement ID to grab.
    :param optim_id: (str) Optimizer iteration to grab.
    :return: (list) List containing the .npz data and the corresponding measurement information.
    """
    data = []
    for path in measurement_path:
        files = os.listdir(path)
        files = [x for x in files if ('.npz' in x) and (x.split('_')[0].isdigit())]
        files.sort(key=lambda x: int(x.split('_')[0]))
        if (meas_id is not None) and (optim_id is not None):
            data.append([[np.load(os.path.join(path, x)), x] for x in files if
                         (x.split('_')[0] == str(meas_id)) and (x.split('_')[1] == str(optim_id))])
        elif meas_id is not None:
            data.append([[np.load(os.path.join(path, x)), x] for x in files if
                         (x.split('_')[1] == str(meas_id))])
        else:
            data.append([[np.load(os.path.join(path, x)), x] for x in files])
    return data


if __name__ == '__main__':
    # path = create_measurement('Test2', hardwarefile='test_hardware', LP=0.9)
    # f = np.linspace(0, 4 * np.pi, 1000)
    # s = np.sin(f)
    # save_npz(path, 'test', f=f, s=s)
    path_grabber('20221111', 'rabi', 47)
