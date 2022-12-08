from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
# from qm.simulate.credentials import create_credentials
import matplotlib.pyplot as plt
from configuration import *
from qm import SimulationConfig
from datetime import datetime
import os

from lib.sequences import setup_qm


def dbmToV(powerInDbm):  # Convert dBm to V
    V = np.power(10, (powerInDbm - 10) / 20)
    return V


def hrDiff(timeInit, timeEnd):  # Find hour difference between two time strings
    dM = int(timeInit.strftime('%M'))
    dH = int(timeInit.strftime('%H'))
    fM = int(timeEnd.strftime('%M'))
    fH = int(timeEnd.strftime('%H'))
    if fM - dM >= 0:
        hh = np.remainder(fH - dH, 24)
    else:
        hh = np.remainder(fH - dH - 1, 24)
    return hh


def timerFunc(timeInit, timeEnd):  # Return the timer string for two time strings
    dM = int(timeInit.strftime('%M'))
    dH = int(timeInit.strftime('%H'))
    dS = int(timeInit.strftime('%S'))
    fM = int(timeEnd.strftime('%M'))
    fH = int(timeEnd.strftime('%H'))
    fS = int(timeEnd.strftime('%S'))

    ss = np.remainder(fS - dS, 60)
    if fS - dS >= 0:
        mm = np.remainder(fM - dM, 60)
    else:
        mm = np.remainder(fM - dM, 60) - 1
    if fM - dM >= 0:
        hh = np.remainder(fH - dH, 24)
    else:
        hh = np.remainder(fH - dH, 24) - 1
    stringToReturn = f'{hh:02d}' + ':' + f'{mm:02d}' + ':' + f'{ss:02d}'
    return stringToReturn


################################
# Open quantum machine manager #
################################
qmm = QuantumMachinesManager(host="192.168.1.254", port='80')
#long_meas_len = 1e7
powerToMeasure = -10  # The power that will be fed from the OPX
# Get the voltage going in and coming out
mw_amp_VSi = dbmToV(powerToMeasure)
powerComingOut = dbmToV(powerToMeasure + 44)
print('Power Coming Out: ' + str(powerComingOut) + ' V')
print('Power Going In: ' + str(mw_amp_VSi) + ' V')

# Prepare nametag to save the file
laserPower = 38
X = 2738.2
Y = 3003.5
Z = 1665.6
fieldX = 24.292
fieldY = 19.324
nameForFile = 'odmr_withoutmw_' + str(powerToMeasure) + 'dBm_Laser_' + str(laserPower) + 'mW_X_' + str(X) + '_Y_' + str(
    Y) + '_Z_' + str(Z) + '_Field_X_' + str(fieldX) + '_Y_' + str(fieldY)

f_vec = np.arange(280e6, 320e6 + 0.1, 2e6)
f_vec = [int(x) for x in f_vec]
sizeOfFrequencyArray = np.shape(f_vec)[0]
initCounts = np.zeros(sizeOfFrequencyArray,
                      dtype=int).tolist()  # Initial counts (later will be integrated if optimizer reforcus is added)

with program() as cw_odmr:
    # Declare QUA variables
    ###################
    signal_st = declare_stream()  # stream for counts
    signal = declare(int)  # variable for number of counts
    signal_Arr = declare(int, value=initCounts)  # attay for adding up counts
    timestamps = declare(int, size=100)  # Timestamp
    n = declare(int, value=0)  # number of iterations
    n_st = declare_stream()  # stream for number of iterations
    f_index = declare(int)  # Index for frequency array
    f = declare(int, value=f_vec)  # frequency array
    # Pulse sequence
    ################
    with infinite_loop_():
        assign(n, n + 1)  # Increase number of iteration
        with for_(f_index, 0, f_index < sizeOfFrequencyArray, f_index + 1):
            update_frequency('NV', f[f_index])  # updated frequency
            align()  # align all elements

            play('const', 'NV', duration=int(long_meas_len // 4))  # play microwave pulse
            play('laser_ON', 'AOM', duration=int(long_meas_len // 4))  # Photoluminescence
            measure('readout_cw', 'APD', None,
                    time_tagging.analog(timestamps, long_meas_len, signal))  # Reading of counts

            assign(signal_Arr[f_index], signal_Arr[
                f_index] + signal)  # Summing up the counts from this iteration with that obtained from previous iteration
            save(signal_Arr[f_index], signal_st)  # save summed up counts array on stream
            save(f[f_index], signal_st)  # save Frequency on stream
        save(n, n_st)  # save number of iteration inside for_loop

    # Stream processing
    ###################
    with stream_processing():
        signal_st.buffer(len(f_vec), 2).save('signal')  # 2 Dimensional buffer to store the frequency and the counts
        n_st.save('iteration')
#######################
# Simulate or execute #
#######################

qmm, qm = setup_qm()
job = qm.execute(cw_odmr)  # execute QUA program
numOptimizerIter = 1
res_handle = job.result_handles  # get access to handles
vec_handle = res_handle.get('signal')
vec_handle.wait_for_values(1)
iteration_handle = res_handle.get('iteration')
iteration_handle.wait_for_values(1)
temp = np.zeros(np.shape(f_vec), dtype=int)
timerBegin = datetime.now()
timerAfterOptimizerIter = datetime.now()
now = datetime.now()
d1 = now.strftime('%Y%m%d_%H%M%S_')
d2 = now.strftime('C:/Data/%Y')
d2m = now.strftime('/%m')
d2d = now.strftime('/%Y%m%d')
if os.path.isdir(d2):
    pass
else:
    os.mkdir(d2)
if os.path.isdir(d2 + d2m):
    pass
else:
    os.mkdir(d2 + d2m)
if os.path.isdir(d2 + d2m + d2d):
    pass
else:
    os.mkdir(d2 + d2m + d2d)
try:
    while vec_handle.is_processing():
        try:
            signalRecord = vec_handle.fetch_all()
            signalRecordSort = signalRecord[signalRecord[:, 0].argsort()]
            frequencyArray = signalRecordSort[:, 0]

            signal = signalRecordSort[:, 1]
            signal = signal/np.max(signal)
            iteration = iteration_handle.fetch_all() + 1
            noiseFloor = signal.max() - np.sqrt(signal.max())
            noiseFloorArray = np.ones(np.shape(f_vec)) * noiseFloor


        except:
            pass
        else:
            timerUpdate = datetime.now()
            timerStr = timerFunc(timerBegin, timerUpdate)
            hrDifference = hrDiff(timerAfterOptimizerIter, timerUpdate)
            freqVecFloat = np.array(f_vec, dtype=float) * 1e-6
            plt.plot(freqVecFloat, signal)  # a.u.
            # plt.plot(freqVecFloat, noiseFloorArray/iteration, color='r')
            plt.legend(['Data', 'Noise floor'])
            plt.xlabel('Frequency [MHz]')
            plt.ylabel('Sum of counts')
            plt.title(f'ODMR after ' + timerStr)
            if hrDifference > 1:
                now = datetime.now()
                d1 = now.strftime('%Y%m%d_%H%M%S_')

                d2 = now.strftime('C:/Data/%Y')
                d2m = now.strftime('/%m')
                d2d = now.strftime('/%Y%m%d')
                if os.path.isdir(d2):
                    pass
                else:
                    os.mkdir(d2)
                if os.path.isdir(d2 + d2m):
                    pass
                else:
                    os.mkdir(d2 + d2m)
                if os.path.isdir(d2 + d2m + d2d):
                    pass
                else:
                    os.mkdir(d2 + d2m + d2d)

                nameForFileSave = d2 + d2m + d2d + '/' + str(
                    numOptimizerIter) + '_' + d1 + nameForFile + '_Iterations_' + str(iteration) + '.png'
                nameForFileSavePdf = d2 + d2m + d2d + '/' + str(
                    numOptimizerIter) + '_' + d1 + nameForFile + '_Iterations_' + str(iteration) + '.pdf'
                nameForFileSaveSvg = d2 + d2m + d2d + '/' + str(
                    numOptimizerIter) + '_' + d1 + nameForFile + '_Iterations_' + str(iteration) + '.svg'
                nameForFileSaveSvz = d2 + d2m + d2d + '/' + str(
                    numOptimizerIter) + '_' + d1 + nameForFile + '_Iterations_' + str(iteration)
                numOptimizerIter = numOptimizerIter + 1
                timerAfterOptimizerIter = datetime.now()
            plt.pause(0.1)
            plt.clf()
            """nameFortxt = d2 + d2m + d2d + '/' +d1 + nameForFile+'_CheckForBufferInteraction.txt'
            nameFortxtSorted = d2 + d2m + d2d + '/' + d1 + nameForFile + '_CheckForBufferInteractionSorted.txt'
            with open(nameFortxt, 'a+') as file_object:
                file_object.seek(0)
                data = file_object.read(100)
                if len(data)>0:
                    file_object.write('\n')
                stringToWrite = '\n'.join('\t'.join('%d' % x for x in y) for y in signalRecord.transpose())
                file_object.write(stringToWrite)
            with open(nameFortxtSorted, 'a+') as file_object:
                file_object.seek(0)
                data = file_object.read(100)
                if len(data)>0:
                    file_object.write('\n')
                stringToWrite = '\n'.join('\t'.join('%d' % x for x in y) for y in signalRecordSort.transpose())
                file_object.write(stringToWrite)"""
except KeyboardInterrupt:
    plt.close('all')
    signalRecord = vec_handle.fetch_all()
    signalRecordSort = signalRecord[signalRecord[:, 0].argsort()]
    frequencyArray = signalRecordSort[:, 0]

    signal = signalRecordSort[:, 1]
    iteration = iteration_handle.fetch_all() + 1
    noiseFloor = signal.max() - np.sqrt(signal.max())
    noiseFloorArray = np.ones(np.shape(f_vec)) * noiseFloor

    timerUpdate = datetime.now()
    timerStr = timerFunc(timerBegin, timerUpdate)
    plt.plot(np.array(f_vec, dtype=float) * 1e-6, signal / iteration)  # a.u.
    plt.plot(np.array(f_vec, dtype=float) * 1e-6, noiseFloorArray / iteration, color='r')
    plt.legend(['Data', 'Noise floor'])
    plt.xlabel('Frequency [MHz]')
    plt.ylabel('Sum of counts')
    plt.title(f'ODMR after ' + timerStr)
    now = datetime.now()
    d1 = now.strftime('%Y%m%d_%H%M%S_')

    d2 = now.strftime('C:/Data/%Y')
    d2m = now.strftime('/%m')
    d2d = now.strftime('/%Y%m%d')
    if os.path.isdir(d2):
        pass
    else:
        os.mkdir(d2)
    if os.path.isdir(d2 + d2m):
        pass
    else:
        os.mkdir(d2 + d2m)
    if os.path.isdir(d2 + d2m + d2d):
        pass
    else:
        os.mkdir(d2 + d2m + d2d)

    nameForFileSave = d2 + d2m + d2d + '/' + d1 + nameForFile + '_Iterations_' + str(iteration) + '.png'
    nameForFileSavePdf = d2 + d2m + d2d + '/' + d1 + nameForFile + '_Iterations_' + str(iteration) + '.pdf'
    nameForFileSaveSvg = d2 + d2m + d2d + '/' + d1 + nameForFile + '_Iterations_' + str(iteration) + '.svg'
    nameForFileSaveSvz = d2 + d2m + d2d + '/' + d1 + nameForFile + '_Iterations_' + str(iteration)

    plt.savefig(nameForFileSave)
    plt.savefig(nameForFileSavePdf)
    plt.savefig(nameForFileSaveSvg)
    np.savez(nameForFileSaveSvz, signal / iteration, np.array(f_vec, dtype=float) * 1e-6)
    plt.close('all')
    """with open(nameFortxt, 'a+') as file_object:
        file_object.seek(0)
        data = file_object.read(100)
        if len(data) > 0:
            file_object.write('\n')
        stringToWrite = '\n'.join('\t'.join('%d' % x for x in y) for y in signalRecord.transpose())
        file_object.write(stringToWrite)"""
    job.halt()
    qm.close()
