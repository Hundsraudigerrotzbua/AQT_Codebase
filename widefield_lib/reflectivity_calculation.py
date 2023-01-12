import numpy as np
import matplotlib.pyplot as plt
import matplotlib

font = {#'family': 'normal',
    # 'weight' : 'bold',
    'size': 25}
matplotlib.rc('font', **font)

n1 = 1
n2 = 2.42
theta_i = np.linspace(0, 90, 300)


def R_n_T(n1, n2, theta_i):
    R_s = np.abs((n1 * np.cos(np.deg2rad(theta_i)) - n2 * np.sqrt(1 - (n1 / n2 * np.sin(np.deg2rad(theta_i))) ** 2)) / (
            n1 * np.cos(np.deg2rad(theta_i)) + n2 * np.sqrt(1 - (n1 / n2 * np.sin(np.deg2rad(theta_i))) ** 2))) ** 2
    R_p = np.abs((n1 * np.sqrt(1 - (n1 / n2 * np.sin(np.deg2rad(theta_i))) ** 2) - n2 * np.cos(np.deg2rad(theta_i))) / (
            n1 * np.sqrt(1 - (n1 / n2 * np.sin(np.deg2rad(theta_i))) ** 2) + n2 * np.cos(np.deg2rad(theta_i)))) ** 2
    R_eff = 0.5 * (R_s + R_p)
    T_eff = 1 - R_eff
    return R_eff, T_eff

def calc_theta(n1, n2, theta_i):
    return np.rad2deg(np.arcsin(n1 / n2 * np.sin(np.deg2rad(theta_i))))


n_glue = np.linspace(1.45, 2.2, 100)
theta_arr = [18, 25]
fig, ax = plt.subplots(1,1)
ax2 = ax.twinx()
for theta_initial in theta_arr:
    theta_dia = []
    theta_glue_arr = []
    theta_glass_vert_arr = []
    T_dia = []
    for n in n_glue:
        n_seq = [1, 1.5, n, 2.42]

        theta_glass = calc_theta(n_seq[0], n_seq[1], theta_initial)
        theta_glass_vert = 90-theta_glass
        theta_glass_vert_arr.append(theta_glass_vert)
        theta_glue = calc_theta(n_seq[1], n_seq[2], theta_glass_vert)
        theta_glue_arr.append(theta_glue)
        theta_dia.append(calc_theta(n_seq[2], n_seq[3], theta_glue))

        T_dia.append(R_n_T(n_seq[0], n_seq[1], theta_initial)[1] * R_n_T(n_seq[1], n_seq[2], theta_glass_vert)[1] * \
                R_n_T(n_seq[2], n_seq[3], theta_glue)[1])

    ax.plot(n_glue, T_dia, 'r', label='Transmitted Power', linewidth=4)
    ax2.plot(n_glue, theta_dia, 'b', label='Angle in diamond', linewidth=4)
    ax.axvline(1.48, linewidth=4)
    ax.axvline(n_glue[np.nanargmax(T_dia)], linewidth=4, linestyle='--', color='k')

ax.tick_params(axis='x', direction='in', length=8, width=3)
ax.tick_params(axis='y', direction='in', length=8, width=3)
ax.set_xlabel('Refractive Index of glue')
ax.set_ylabel('Transmitted Power (red)')
ax2.set_ylabel('Angle in diamond (blue)')
plt.minorticks_on()
plt.grid(which='major', linewidth=1)
plt.grid(which='minor', linewidth=1, linestyle='--')
plt.legend(loc='upper right')
manager = plt.get_current_fig_manager()
manager.window.showMaximized()
plt.tight_layout()
plt.show()