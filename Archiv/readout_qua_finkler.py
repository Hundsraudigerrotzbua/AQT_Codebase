def readout_qua(result1, result2, result_len1, result_len2, meas_len, rabi_vec, t_ind, m):

    wait(100 // 4, 'laser')
    play('rabi', 'laser', duration=(meas_len - 400) // 4)
    measure('rabi', 'readout1', None, time_tagging.raw(result1, meas_len, targetLen=result_len1))
    measure('rabi', 'readout2', None, time_tagging.raw(result2, meas_len, targetLen=result_len2))  # 1ns

    with for_(m, 0, m < result_len1, m + 1):
        with if_((result1[m] > 220) & (result1[m] < 400)):
            assign(rabi_vec[t_ind], rabi_vec[t_ind] + 1)

    with for_(m, 0, m < result_len2, m + 1):
        with if_((result2[m] > 220) & (result2[m] < 400)):
            assign(rabi_vec[t_ind], rabi_vec[t_ind] + 1)
