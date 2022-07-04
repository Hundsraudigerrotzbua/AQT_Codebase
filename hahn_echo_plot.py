import matplotlib

matplotlib.use("TkAgg")
from lib.QuantechPlots import *
import os

dir_path = 'D:\\QM_OPX_Fiona\\Data\\2022-05-04\\Mikrowelle_an'
dir = os.listdir(dir_path)
for file in dir:
    if file.endswith('.npz'):
        data = np.load(os.path.join(dir_path, file), allow_pickle=True)
        #fig, ax = plt.subplots()
        hahn_echo_plot(data[0], data[1], data[2], T2_guess=100, devi_plot=True)
        plt.title(f'{file}')