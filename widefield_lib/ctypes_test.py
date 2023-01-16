import ctypes
import numpy as np
from configuration_widefield import cm_total_frames, cm_exposure_time, cm_EM_Gain, cm_file_name

"""
Test script to get familiar with ctypes functionality with precompiled C++ libraries.
Confirmed working.

Persisting problem:

In order to get a reproducible sequence start the widefield_odmr.py needs to be executed once the camera is ready. 
This can either be read out through the software return of the API or a digital channel - since the OPX only offers 2 
analog inputs and 1 digital input, which are all in use, the software solution has to be used.
"""

# Compiled with g++ -shared -fPIC -ID:\\Widefield\\Code\\PICAM_samples\\includes -LD:\\Widefield\\Code\\PICAM_samples\\libraries64 shared_lib.cpp -o test_compile2.so -lPicam
path_to_lib = 'D:\\Widefield\\Code\\PICAM_Code\\test_compile3.so'
lib = ctypes.cdll.LoadLibrary(path_to_lib)
lib.main.restype = ctypes.c_int
lib.main.argtypes = ctypes.c_int, ctypes.POINTER(ctypes.c_char_p)
#args = (ctypes.c_char_p * 4)(b'300', b'100', b'10', b'D:\\Widefield\\Daten\\telescope_max_focus\\ctypes_test_final.raw')
args = (ctypes.c_char_p * 4)(str(cm_total_frames).encode(), str(cm_exposure_time).encode(), str(cm_EM_Gain).encode(), cm_file_name.encode())
print(lib.main(len(args), args))








#path_to_lib = 'D:\\Widefield\\Code\\PICAM_Code\\shared_lib.so'
#lib = ctypes.cdll.LoadLibrary(path_to_lib)
#print(lib.main())
