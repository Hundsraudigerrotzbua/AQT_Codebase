from scipy.optimize import curve_fit
from lmfit import Model
import numpy as np


def ODMR_fit_func(x, C, gam, xc):
    return 1 - C * (gam ** 2 / (4 * (x - xc) ** 2 + gam ** 2))


def fit_odmr(f_vec, data, guess):
    fit_val, fit_cov = curve_fit(ODMR_fit_func, f_vec, data, p0=guess, method='trf')
    return fit_val


def rabi_fit_func(x, lam, amp, freq, phi, off):
    return np.exp(-lam * x) * (amp * np.sin(2 * np.pi * freq * x + phi)) + off

def ramsey_fit_func( x, amp, lam, n, off):
    return amp*np.exp(-(lam*x)**n) + off

def fit_rabi(t_vec, data, lam_g=1e-9, amp_g=1, freq_g=1 / 500, phi_g=0, off_g=0.9):
    dec_model = Model(rabi_fit_func, nan_policy='propagate')
    results = dec_model.fit(data, x=t_vec, lam=lam_g, amp=amp_g, freq=freq_g, phi=phi_g, off=off_g)
    return results.best_fit, np.round(1/results.params['freq'].value / 2, 1)

def fit_ramsey(t_vec, data, amp_g=1, lam_g=1/500, n_g=1, off_g=0):
    dec_model = Model(ramsey_fit_func, nan_policy='propagate')
    results = dec_model.fit(data, x=t_vec, lam=lam_g, amp=amp_g, n=n_g, off=off_g)
    return results.best_fit
