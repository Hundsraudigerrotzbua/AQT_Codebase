import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import numpy as np
import os
from lib.fit_lib import *

font = {'family': 'normal',
        # 'weight' : 'bold',
        'size': 35}
matplotlib.rc('font', **font)




def plot_odmr(f_vec, data, lw=4, no_save=0, save='D:\\QM_OPX\\OPX_Lib_WIP\\Data\\DATADUMP_DONT_USE\\NOPE.pdf', fit=0):
    """ By A.P.
    Saves ODMR Data handed to the function in a specific format.
    :param f_vec: (np.array, list of np.arrays) Frequency Data of ODMR
    :param data: (np.array, list of np.arrays) Signal Data of ODMR
    :param lw: (int) Linewidth of plot
    :param save: (str) Path to the file to save to.
    :param no_save: (Bool) Set to True to not save.
    :return: fig, AX: Figure und Axes of the generated plot.
    """
    xlabel = 'MW Frequency [GHz]'
    ylabel = 'Spin Contrast [arb. u.]'
    title = f'CW-ODMR'
    if (type(f_vec) == list and type(data) == list):
        fig, AX = plt.subplots(len(f_vec), 1)
        for idx in range(0, len(f_vec)):
            norm_data = data[idx] / np.max(data[idx])
            AX[idx].scatter(np.array(f_vec) * 1e-9 + 2.57, norm_data, linewidth=lw)
            fhwm = [x for x in range(len(norm_data)) if
                    norm_data[x] < max(norm_data) - (max(norm_data) - min(norm_data)) / 2]
            fit_guess = [norm_data.max() - norm_data.min(), max(fhwm) - min(fhwm),
                         min((val, idx) for (idx, val) in enumerate(norm_data))[1]]
            fit = fit_odmr(np.array(f_vec) * 1e-9 + 2.57, norm_data, fit_guess)
            AX[idx].plot(np.array(f_vec) * 1e-9 + 2.57,
                         ODMR_fit_func(np.array(f_vec) * 1e-9 + 2.57, fit[0], fit[1], fit[2]), linewidth=lw // 2,
                         color='orange')
            AX[idx].axvline(x=2.87, color='k', linewidth=lw // 2, linestyle='--')
            AX[idx].set_xlabel(xlabel)
            AX[idx].set_ylabel(ylabel)
        AX[0].set_title(title)
    else:
        fig, AX = plt.subplots(1, 1)
        norm_data = data / np.max(data)
        f_vec = np.array(f_vec) * 1e-9 + 2.57
        AX.scatter(f_vec, norm_data, linewidth=lw)
        if fit:
            fhwm = [x for x in range(len(norm_data)) if
                    norm_data[x] < max(norm_data) - (max(norm_data) - min(norm_data)) / 2]
            fit_guess = [norm_data.max() - norm_data.min(),
                         f_vec[max(fhwm)] - f_vec[min(fhwm)],
                         f_vec[min((val, idx) for (idx, val) in enumerate(norm_data))[1]]]
            fit = fit_odmr(f_vec, norm_data, fit_guess)
            fit_f_vec = np.linspace(f_vec[0], f_vec[-1], 1000)
            AX.plot(fit_f_vec, ODMR_fit_func(fit_f_vec, fit[0], fit[1], fit[2]),
                    linewidth=lw, color='red')
        AX.axvline(x=2.87, color='k', linewidth=lw // 2, linestyle='--')
        AX.set_xlabel(xlabel)
        AX.set_ylabel(ylabel)
        for side in AX.spines.keys():
            AX.spines[side].set_linewidth(3)
        AX.yaxis.set_ticks(np.flip(np.arange(1, min(norm_data) - 0.05, -0.05)))
        AX.tick_params(axis='x', direction='in', length=8, width=3)
        AX.tick_params(axis='y', direction='in', length=8, width=3)
        AX.set_title(title)
    plt.minorticks_on()
    AX.xaxis.set_minor_locator(AutoMinorLocator(2))
    AX.yaxis.set_minor_locator(AutoMinorLocator(2))
    plt.grid(which='major', linewidth=1)
    plt.grid(which='minor', linewidth=1, linestyle='--')
    plt.tight_layout()
    fig.set_size_inches(22, 18)
    if not no_save:
        plt.savefig(save, bbox_inches='tight')  # , transparent=True)
        print(f'Saved Figure to {save}.')
    return fig, AX


def plot_odmr_live(f_vec, data, fig=None, AX=None, lw=4, elapsed_iterations=0):
    """ By A.P.
    Saves ODMR Data handed to the function in a specific format.
    :param f_vec: (np.array, list of np.arrays) Frequency Data of ODMR
    :param data: (np.array, list of np.arrays) Signal Data of ODMR
    :param lw: (int) Linewidth of plot
    :param save: (str) Path to the file to save to.
    :param no_save: (Bool) Set to True to not save.
    :return: fig, AX: Figure und Axes of the generated plot.
    """
    xlabel = 'MW Frequency [GHz]'
    ylabel = 'Spin Contrast [arb. u.]'
    title = f'CW-ODMR Iteration {elapsed_iterations}'
    if (type(f_vec) == list and type(data) == list):
        if (fig is None) or (AX is None):
            fig, AX = plt.subplots(len(f_vec), 1)
        for idx in range(0, len(f_vec)):
            norm_data = data[idx] / np.max(data[idx])
            AX[idx].scatter(np.array(f_vec) * 1e-9 + 2.57, norm_data, linewidth=lw)
            AX[idx].axvline(x=2.87, color='k', linewidth=lw // 2, linestyle='--')
            AX[idx].set_xlabel(xlabel)
            AX[idx].set_ylabel(ylabel)
            [x.grid() for x in AX]
        AX[0].set_title(title)
    else:
        if (fig is None) or (AX is None):
            fig, AX = plt.subplots(1, 1)
        norm_data = data / np.max(data)
        AX.scatter(np.array(f_vec) * 1e-9 + 2.57, norm_data, linewidth=lw)
        AX.axvline(x=2.87, color='k', linewidth=lw // 2, linestyle='--')
        AX.set_xlabel(xlabel)
        AX.set_ylabel(ylabel)
        AX.set_title(title)
        for side in AX.spines.keys():
            AX.spines[side].set_linewidth(3)
        AX.yaxis.set_ticks(np.flip(np.arange(1, min(norm_data) - 0.05, -0.05)))
        AX.tick_params(axis='x', direction='in', length=8, width=3)
        AX.tick_params(axis='y', direction='in', length=8, width=3)
        AX.set_title(title)
    plt.minorticks_on()
    AX.xaxis.set_minor_locator(AutoMinorLocator(2))
    AX.yaxis.set_minor_locator(AutoMinorLocator(2))
    plt.grid(which='major', linewidth=1)
    plt.grid(which='minor', linewidth=1, linestyle='--')
    plt.tight_layout()
    # fig.set_size_inches(22, 18)
    # manager = plt.get_current_fig_manager()
    # manager.window.showMaximized()
    plt.pause(0.1)
    if type(AX) is tuple:
        AX[0].clear()
        AX[1].clear()
    else:
        AX.clear()
    return fig, AX


def plot_rabi(t_vec, data, lw=4, no_save=0, save='D:\\QM_OPX\\OPX_Lib_WIP\\Data\\DATADUMP_DONT_USE\\NOPE.pdf', fit=0):
    xlabel = r'Pulse Length $\tau$ [ns]'
    ylabel = 'Spin Contrast [arb. u.]'
    title = f'Time Rabi'
    fig, ax = plt.subplots(1, 1)
    t_vec = 4 * np.array(t_vec)
    data_norm = data/np.max(data)
    ax.scatter(t_vec, data_norm, linewidth=lw, label='Data')
    if fit:
        yf, t_rabi = fit_rabi(t_vec, data_norm, amp_g=data_norm[0], off_g=np.mean(data_norm))
        ax.plot(t_vec, yf, label='Fit')
    for side in ax.spines.keys():
        ax.spines[side].set_linewidth(3)
    ax.yaxis.set_ticks(np.flip(np.arange(1, min(data_norm) - 0.05, -0.05)))
    ax.tick_params(axis='x', direction='in', length=8, width=3)
    ax.tick_params(axis='y', direction='in', length=8, width=3)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.minorticks_on()
    ax.xaxis.set_minor_locator(AutoMinorLocator(2))
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    plt.grid(which='major', linewidth=1)
    plt.grid(which='minor', linewidth=1, linestyle='--')
    plt.legend()
    plt.tight_layout()
    fig.set_size_inches(22, 18)
    if not no_save:
        plt.savefig(save, bbox_inches='tight')  # , transparent=True)
        print(f'Saved Figure to {save}.')
    return fig, ax


def plot_rabi_live(t_vec, data, lw=4, fig=None, ax=None, elapsed_iterations=0):
    xlabel = r'Pulse Length $\tau$ [ns]'
    ylabel = 'Spin Contrast [arb. u.]'
    title = f'Time Rabi Iteration {elapsed_iterations}'
    t_vec = 4 * np.array(t_vec)
    ax.scatter(t_vec, data / np.max(data), linewidth=lw)
    for side in ax.spines.keys():
        ax.spines[side].set_linewidth(3)
    ax.yaxis.set_ticks(np.flip(np.arange(1, min(data / np.max(data)) - 0.05, -0.05)))
    ax.tick_params(axis='x', direction='in', length=8, width=3)
    ax.tick_params(axis='y', direction='in', length=8, width=3)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.minorticks_on()
    ax.xaxis.set_minor_locator(AutoMinorLocator(2))
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    plt.grid(which='major', linewidth=1)
    plt.grid(which='minor', linewidth=1, linestyle='--')
    plt.tight_layout()
    plt.pause(0.1)
    if type(ax) is tuple:
        ax[0].clear()
        ax[1].clear()
    else:
        ax.clear()
    return fig, ax


def plot_ramsey(t_vec, counts, counts2, lw=4, no_save=0,
                save='D:\\QM_OPX\\OPX_Lib_WIP\\Data\\DATADUMP_DONT_USE\\NOPE.pdf', fit=0):
    xlabel = r'Dephasing Time $\tau$ [ns]'
    ylabel = 'Spin Contrast [arb. u.]'
    title = f'Ramsey'
    fig, ax = plt.subplots(1, 1)
    t_vec = 4 * np.array(t_vec)
    data = counts - counts2
    ax.scatter(t_vec, data/np.max(data), linewidth=lw)
    for side in ax.spines.keys():
        ax.spines[side].set_linewidth(3)
    #ax.yaxis.set_ticks(np.flip(np.arange(1, min(data / np.max(data)) - 0.05, -0.05)))
    ax.tick_params(axis='x', direction='in', length=8, width=3)
    ax.tick_params(axis='y', direction='in', length=8, width=3)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.minorticks_on()
    ax.xaxis.set_minor_locator(AutoMinorLocator(2))
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    plt.grid(which='major', linewidth=1)
    plt.grid(which='minor', linewidth=1, linestyle='--')
    plt.tight_layout()
    fig.set_size_inches(22, 18)
    if not no_save:
        plt.savefig(save, bbox_inches='tight')  # , transparent=True)
        print(f'Saved Figure to {save}.')
    return fig, ax


def plot_ramsey_live(t_vec, counts, counts2, lw=4, fig=None, ax=None, elapsed_iterations=0):
    xlabel = r'Dephasing Time $\tau$ [ns]'
    ylabel = 'Spin Contrast [arb. u.]'
    title = f'Ramsey Iteration {elapsed_iterations}'
    t_vec = 4 * np.array(t_vec)
    #    ax.scatter(t_vec, data/np.max(data), linewidth=lw)
    data = counts - counts2
    ax.scatter(t_vec, data/np.max(data), linewidth=lw)
    for side in ax.spines.keys():
        ax.spines[side].set_linewidth(3)
        #ax.yaxis.set_ticks(np.flip(np.arange(1, min(data/np.max(data))-0.05, -0.05)))
    ax.tick_params(axis='x', direction='in', length=8, width=3)
    ax.tick_params(axis='y', direction='in', length=8, width=3)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.minorticks_on()
    ax.xaxis.set_minor_locator(AutoMinorLocator(2))
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    plt.grid(which='major', linewidth=1)
    plt.grid(which='minor', linewidth=1, linestyle='--')
    plt.tight_layout()
    plt.pause(0.1)
    if type(ax) is tuple:
        ax[0].clear()
        ax[1].clear()
    else:
        ax.clear()
    return fig, ax


def plot_pulsed_odmr(f_vec, data, lw=4, no_save=0, save='D:\\QM_OPX\\OPX_Lib_WIP\\Data\\DATADUMP_DONT_USE\\NOPE.pdf',
                     fit=0):
    """ By A.P.
    Saves ODMR Data handed to the function in a specific format.
    :param f_vec: (np.array, list of np.arrays) Frequency Data of ODMR
    :param data: (np.array, list of np.arrays) Signal Data of ODMR
    :param lw: (int) Linewidth of plot
    :param save: (str) Path to the file to save to.
    :param no_save: (Bool) Set to True to not save.
    :return: fig, AX: Figure und Axes of the generated plot.
    """
    xlabel = 'MW Frequency [GHz]'
    ylabel = 'Spin Contrast [arb. u.]'
    title = f'Pulsed-ODMR'
    if (type(f_vec) == list and type(data) == list):
        fig, AX = plt.subplots(len(f_vec), 1)
        for idx in range(0, len(f_vec)):
            norm_data = data[idx] / np.max(data[idx])
            AX[idx].scatter(np.array(f_vec) * 1e-9 + 2.57, norm_data, linewidth=lw)
            fhwm = [x for x in range(len(norm_data)) if
                    norm_data[x] < max(norm_data) - (max(norm_data) - min(norm_data)) / 2]
            fit_guess = [norm_data.max() - norm_data.min(), max(fhwm) - min(fhwm),
                         min((val, idx) for (idx, val) in enumerate(norm_data))[1]]
            fit = fit_odmr(np.array(f_vec) * 1e-9 + 2.57, norm_data, fit_guess)
            AX[idx].plot(np.array(f_vec) * 1e-9 + 2.57,
                         ODMR_fit_func(np.array(f_vec) * 1e-9 + 2.57, fit[0], fit[1], fit[2]), linewidth=lw // 2,
                         color='orange')
            AX[idx].axvline(x=2.87, color='k', linewidth=lw // 2, linestyle='--')
            AX[idx].set_xlabel(xlabel)
            AX[idx].set_ylabel(ylabel)
        AX[0].set_title(title)
    else:
        fig, AX = plt.subplots(1, 1)
        norm_data = data / np.max(data)
        f_vec = np.array(f_vec) * 1e-9 + 2.57
        AX.scatter(f_vec, norm_data, linewidth=lw)
        if fit:
            fhwm = [x for x in range(len(norm_data)) if
                    norm_data[x] < max(norm_data) - (max(norm_data) - min(norm_data)) / 2]
            fit_guess = [norm_data.max() - norm_data.min(),
                         f_vec[max(fhwm)] - f_vec[min(fhwm)],
                         f_vec[min((val, idx) for (idx, val) in enumerate(norm_data))[1]]]
            fit = fit_odmr(f_vec, norm_data, fit_guess)
            fit_f_vec = np.linspace(f_vec[0], f_vec[-1], 1000)
            AX.plot(fit_f_vec, ODMR_fit_func(fit_f_vec, fit[0], fit[1], fit[2]),
                    linewidth=lw, color='red')
        AX.axvline(x=2.87, color='k', linewidth=lw // 2, linestyle='--')
        AX.set_xlabel(xlabel)
        AX.set_ylabel(ylabel)
        for side in AX.spines.keys():
            AX.spines[side].set_linewidth(3)
        AX.yaxis.set_ticks(np.flip(np.arange(1, min(norm_data) - 0.05, -0.05)))
        AX.tick_params(axis='x', direction='in', length=8, width=3)
        AX.tick_params(axis='y', direction='in', length=8, width=3)
        AX.set_title(title)
    plt.minorticks_on()
    AX.xaxis.set_minor_locator(AutoMinorLocator(2))
    AX.yaxis.set_minor_locator(AutoMinorLocator(2))
    plt.grid(which='major', linewidth=1)
    plt.grid(which='minor', linewidth=1, linestyle='--')
    plt.tight_layout()
    fig.set_size_inches(22, 18)
    if not no_save:
        plt.savefig(save, bbox_inches='tight')  # , transparent=True)
        print(f'Saved Figure to {save}.')
    return fig, AX


def plot_pulsed_odmr_live(f_vec, data, fig=None, AX=None, lw=4, elapsed_iterations=0):
    """ By A.P.
    Saves ODMR Data handed to the function in a specific format.
    :param f_vec: (np.array, list of np.arrays) Frequency Data of ODMR
    :param data: (np.array, list of np.arrays) Signal Data of ODMR
    :param lw: (int) Linewidth of plot
    :param save: (str) Path to the file to save to.
    :param no_save: (Bool) Set to True to not save.
    :return: fig, AX: Figure und Axes of the generated plot.
    """
    xlabel = 'MW Frequency [GHz]'
    ylabel = 'Spin Contrast [arb. u.]'
    title = f'Pulsed-ODMR Iteration {elapsed_iterations}'
    if (type(f_vec) == list and type(data) == list):
        if (fig is None) or (AX is None):
            fig, AX = plt.subplots(len(f_vec), 1)
        for idx in range(0, len(f_vec)):
            norm_data = data[idx] / np.max(data[idx])
            AX[idx].scatter(np.array(f_vec) * 1e-9 + 2.57, norm_data, linewidth=lw)
            AX[idx].axvline(x=2.87, color='k', linewidth=lw // 2, linestyle='--')
            AX[idx].set_xlabel(xlabel)
            AX[idx].set_ylabel(ylabel)
            [x.grid() for x in AX]
        AX[0].set_title(title)
    else:
        if (fig is None) or (AX is None):
            fig, AX = plt.subplots(1, 1)
        norm_data = data / np.max(data)
        AX.scatter(np.array(f_vec) * 1e-9 + 2.57, norm_data, linewidth=lw)
        AX.axvline(x=2.87, color='k', linewidth=lw // 2, linestyle='--')
        AX.set_xlabel(xlabel)
        AX.set_ylabel(ylabel)
        AX.set_title(title)
        for side in AX.spines.keys():
            AX.spines[side].set_linewidth(3)
        AX.yaxis.set_ticks(np.flip(np.arange(1, min(norm_data) - 0.05, -0.05)))
        AX.tick_params(axis='x', direction='in', length=8, width=3)
        AX.tick_params(axis='y', direction='in', length=8, width=3)
        AX.set_title(title)
    plt.minorticks_on()
    AX.xaxis.set_minor_locator(AutoMinorLocator(2))
    AX.yaxis.set_minor_locator(AutoMinorLocator(2))
    plt.grid(which='major', linewidth=1)
    plt.grid(which='minor', linewidth=1, linestyle='--')
    plt.tight_layout()
    # fig.set_size_inches(22, 18)
    # manager = plt.get_current_fig_manager()
    # manager.window.showMaximized()
    plt.pause(0.1)
    if type(AX) is tuple:
        AX[0].clear()
        AX[1].clear()
    else:
        AX.clear()
    return fig, AX


def plot_histogram():
    return 0


def plot_histogram_live():
    return 0


if __name__ == '__main__':
    path = 'C:\\Data\\OPX_Datadump\\20221109\\odmr_1'
    data = np.load(os.path.join(path, '39_221109-140719.npz'))

    fig, AX = plt.subplots(1, 1)
    _, _ = plot_odmr(data['arr_0'] + 2.57e9, data['arr_1'], no_save=1, fig=fig, AX=AX)
    plt.show()

    # fig, ax = plt.subplots(1,1)
    # ax.plot(data['arr_0']+2.57e9, data['arr_1']/np.max(data['arr_1']))
