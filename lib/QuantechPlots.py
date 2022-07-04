import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import scipy.optimize as so

def hahn_echo_plot(x, s1, s2, T2_guess=100, fit=True, devi_plot=False):
    font = {'family': 'normal',
            # 'weight' : 'bold',
            'size': 25}

    matplotlib.rc('font', **font)
    def func(x, a, b, c):
        return a * np.exp(-x / b) + c

    y = (s1-s2) / np.max(s1-s2)
    plt.plot(x, y, 'o', label='S1-S2')
    if fit:
        try:
            a, b = so.curve_fit(func, x, y, p0=(0.1, T2_guess, 1))
            x_fit = np.linspace(np.min(x), np.max(x), 1000)
            y_fit = func(x_fit, *a)
            plt.plot(x_fit, y_fit, label=f'Exponential Fit')
            plt.axvline(x=a[1], color='k', linestyle='--', label=f'T2 = {np.around(a[1], 1)} ns')
        except:
            print("Couldn't fit to the samples!")
    plt.xlabel(r'Evolution time $\tau$ [ns]')
    plt.ylabel(r'Spin Signal [a.u.]')
    plt.legend()
    if devi_plot:
        fig, ax = plt.subplots()
        plt.plot(x, s1/(520e-9), label='s1')
        plt.plot(x, s2/(520e-9), label='s2')
        plt.xlabel(r'Evolution time $\tau$ [ns]')
        plt.ylabel(r'PL Signal [cps]')
