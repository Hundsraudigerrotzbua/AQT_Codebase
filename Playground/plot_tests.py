from lib.plot_lib import *
from lib.data_handler import file_grabber, path_grabber
import os
import numpy as np
import matplotlib.pyplot as plt


path = path_grabber('20221117', 'ramsey', 3)
file = file_grabber(path, meas_id=0)[0][0][0]

fig, ax = plot_ramsey(file['times'], file['counts'], file['counts2'])
plt.show()