import os
import re
from datetime import datetime
from lib.sequences import *
import pickle as pkl
import scipy.optimize as so


class Measurement:
    script_dir = 'D:\\QM_OPX_FIONA'
    work_dir = os.path.join(script_dir, 'Data')

    def __init__(self, meas_tag):
        self.measurement_label = meas_tag
        self.data = []
        self.date_dir = f'{datetime.today().date()}'
        self.working_dir = os.path.join(self.work_dir, self.date_dir)
        if not os.path.isdir(self.working_dir):
            os.mkdir(self.working_dir)
        self.working_dir = os.path.join(self.working_dir, self.measurement_label)
        if not os.path.isdir(self.working_dir):
            os.mkdir(self.working_dir)

    def add_measurement(self, sequence, *args, **kwargs):
        if sequence.lower() == 'hahn_echo' or sequence.lower() == 'hahn echo':
            t, s1, s2, it = hahn_echo(*args, **kwargs)
            label = f"{datetime.now().strftime('%Y%m%d-%H-%M-%S')}_hahn_echo_{str(args).strip('()').replace(', ', '_')}_{re.sub('[^A-Za-z0-9]+', '', str(kwargs))}"
        elif sequence.lower() == 'rabi':
            t, s1, s2, it = rabi(*args, **kwargs)
            label = f"{datetime.now().strftime('%Y%m%d-%H-%M-%S')}_rabi_{str(args).strip('()').replace(', ', '_')}_{re.sub('[^A-Za-z0-9]+', '', str(kwargs))}"
        elif sequence.lower() == 'ramsey':
            t, s1, s2, it = ramsey(*args, **kwargs)
            label = f"{datetime.now().strftime('%Y%m%d-%H-%M-%S')}_ramsey_{str(args).strip('()').replace(', ', '_')}_{re.sub('[^A-Za-z0-9]+', '', str(kwargs))}"
        else:
            raise ValueError(f'Given Sequence "{sequence}" not found.')
        return self.save_data(label, [t, s1, s2, it])

    def save_data(self, filename, data):
        self.data.append(data)
        with open(os.path.join(self.working_dir, filename+'.npz'), "wb") as f:
            pkl.dump(data, f)
        os.popen(
            f'copy {os.path.join(self.script_dir, "configuration.py")} {os.path.join(self.working_dir,filename+ "_configuration.py")}')
        return 0

    def hahn_echo_decay_fit(self, x, y, T2_guess = 100):
        def func(x, a, b, c):
            return a * np.exp(-x / b) + c

        a, b = so.curve_fit(func, x, y, p0=(0.1, T2_guess, 1))
        return x, func(x, *a), a[1]
