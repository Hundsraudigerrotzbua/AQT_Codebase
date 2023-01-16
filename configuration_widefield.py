"""
Configuration file for the NV Center widefield setup.
"""
import numpy as np
from scipy import signal
from qualang_tools.config.integration_weights_tools import convert_integration_weights

simulate = False
# Frequencies
NV_IF_freq = 200.00e6  # OPX IQ OUTPUT FREQUENCIES in units of Hz
NV_LO_freq = 2.67e9  # WINDFREAK IQ MIXING FREQUENCY in units of Hz
NV_LO_pwr = 13 # WINDFREAK IQ MIXING POWER in dBm

# frequency to be swept over in the ODMR in absolute frequencies
f_vec_array = np.arange(2.67e9, 3.07e9+0.1, 200e6)
#f_vec_array = np.array([2.87e9])

# pulse lengths
camera_trigger_len = 200000  # in ns (200µs)

##################################################################################
# Widefield Camera settings
##################################################################################
cm_exposure_time = 100 # ms
cm_readout_cleaning_time = 90 # ms
cm_EM_Gain = 10
##################################################################################

# MW parameters
#mw_amp_NV = 0.2  # in units of volts
mw_len_NV = 20  # in units of ns

# Integration weights
optimized_weights_list = [1.0] * int(300)
optimized_weights = convert_integration_weights(optimized_weights_list)


def IQ_imbalance(g, phi):
    c = np.cos(phi)
    s = np.sin(phi)
    n = 1 / ((1 - g ** 2) * (2 * c ** 2 - 1))
    return [float(n * x) for x in [(1 - g) * c,(1 + g) * s, (1 - g) * s, (1 + g) * c]]

def create_config(mw_amp_NV=0.2):
    config = {

        'version': 1,

        'controllers': {

            'con1': {
                'type': 'opx1',
                'analog_outputs': {
                    # Both offsets are for 0.2V MW amplitude
                    # On-the-fly-changes:
                    # qm.set_dc_offset_by_qe('NV', 'I', 0.0114)
                    # qm.set_dc_offset_by_qe('NV', 'Q', -0.0024)
                    1: {'offset': 0.01385, 'delay': 73},  # 75},  # NV I for OPX+ 1: {'offset': 0.0, 'delay': 0}
                    2: {'offset': -0.0021, 'delay': 73},  # 75},  # NV Q
                    # 3: {'offset': 0.0},  # Nuclear spin
                    4: {'offset': 0.0},

                },
                'digital_outputs': {
                    2: {},  # AOM/Laser
                    # 3: {},  # MW Trigger
                },
            }
        },

        'elements': {

            'NV': {
                'mixInputs': {
                    'I': ('con1', 1),
                    'Q': ('con1', 2),
                    # 'marker': {
                    #    'port': ('con1', 3),
                    #    'delay': 0,
                    #    'buffer': 0,
                    # },
                    'lo_frequency': NV_LO_freq,
                    'mixer': 'mixer_qubit'
                },
                'intermediate_frequency': NV_IF_freq,
                'operations': {
                    'const': 'NV_cw_pulse',
                    'zero': 'NV_zero_pulse'
                },
                'hold_offset': {
                    'duration': 1
                }
            },

            'camera': {
                'digitalInputs': {
                    'marker': {
                        'port': ('con1', 2),
                        'delay': 0,
                        'buffer': 0,
                    },
                },
                'operations': {
                    'camera_trigger_ON': 'trigger_ON_pulse',
                }
            },
        },

        'pulses': {

            'NV_cw_pulse': {
                'operation': 'control',
                'length': mw_len_NV,
                'waveforms': {
                    "I": "NV_const_wf",
                    "Q": "zero_wf"
                },
                # 'digital_marker': 'ON',
            },
            'NV_zero_pulse': {
                'operation': 'control',
                'length': mw_len_NV,
                'waveforms': {
                    "I": "zero_wf",
                    "Q": "zero_wf"
                },
                # 'digital_marker': 'ON',
            },

            'trigger_ON_pulse': {
                'operation': 'control',
                'length': camera_trigger_len,
                'digital_marker': 'ON',
            },
        },

        'waveforms': {
            'NV_const_wf': {'type': 'constant', 'sample': mw_amp_NV},
            'zero_wf': {'type': 'constant', 'sample': 0.0},
        },

        'digital_waveforms': {
            "ON": {
                "samples": [(1, 0)]  # [(on/off, ns)]
            },
            "OFF": {
                "samples": [(0, 0)]  # [(on/off, ns)]
            }
        },

        'mixers': {
            'mixer_qubit': [
                {'intermediate_frequency': NV_IF_freq, 'lo_frequency': NV_LO_freq,
                 'correction': IQ_imbalance(0.40, -0.11)},  # (Amplitude, Phase) Imbalances!
                # ok-ish for 0.2V 'correction': IQ_imbalance(0.03, -0.115)},  # (Amplitude, Phase) Imbalances!
                # optimized  for 0.45V 'correction': IQ_imbalance(0.2, -0.148)},  # (Amplitude, Phase) Imbalances!
                # 'correction': IQ_imbalance(0.007, 0.0)},  # matched according to oscilloscope - doesnt work tho
                # {'intermediate_frequency': NV_IF_freq, 'lo_frequency': NV_LO_freq, 'correction': IQ_imbalance(0.1, 0.1)},
            ],
        },
    }
    return config


#config = {
#
#    'version': 1,
#
#    'controllers': {
#
#        'con1': {
#            'type': 'opx1',
#            'analog_outputs': {
#                # Both offsets are for 0.2V MW amplitude
#                # On-the-fly-changes:
#                # qm.set_dc_offset_by_qe('NV', 'I', 0.0114)
#                # qm.set_dc_offset_by_qe('NV', 'Q', -0.0024)
#                1: {'offset': 0.01385, 'delay': 73}, #75},  # NV I for OPX+ 1: {'offset': 0.0, 'delay': 0}
#                2: {'offset': -0.0021, 'delay': 73}, #75},  # NV Q
#                #3: {'offset': 0.0},  # Nuclear spin
#                4: {'offset': 0.0},
#
#            },
#            'digital_outputs': {
#                2: {},  # AOM/Laser
#                #3: {},  # MW Trigger
#            },
#        }
#    },
#
#    'elements': {
#
#        'NV': {
#            'mixInputs': {
#                'I': ('con1', 1),
#                'Q': ('con1', 2),
#                #'marker': {
#                #    'port': ('con1', 3),
#                #    'delay': 0,
#                #    'buffer': 0,
#                #},
#                'lo_frequency': NV_LO_freq,
#                'mixer': 'mixer_qubit'
#            },
#            'intermediate_frequency': NV_IF_freq,
#            'operations': {
#                'const': 'NV_cw_pulse',
#                'zero': 'NV_zero_pulse'
#            },
#            'hold_offset': {
#                'duration': 1
#            }
#        },
#
#        'camera': {
#            'digitalInputs': {
#                'marker': {
#                    'port': ('con1', 2),
#                    'delay': 0,
#                    'buffer': 0,
#                },
#            },
#            'operations': {
#                'camera_trigger_ON': 'trigger_ON_pulse',
#            }
#        },
#    },
#
#    'pulses': {
#
#        'NV_cw_pulse': {
#            'operation': 'control',
#            'length': mw_len_NV,
#            'waveforms': {
#                "I": "NV_const_wf",
#                "Q": "zero_wf"
#            },
#            #'digital_marker': 'ON',
#        },
#        'NV_zero_pulse': {
#            'operation': 'control',
#            'length': mw_len_NV,
#            'waveforms': {
#                "I": "zero_wf",
#                "Q": "zero_wf"
#            },
#            # 'digital_marker': 'ON',
#        },
#
#        'trigger_ON_pulse': {
#            'operation': 'control',
#            'length': camera_trigger_len,
#            'digital_marker': 'ON',
#        },
#    },
#
#    'waveforms': {
#        'NV_const_wf': {'type': 'constant', 'sample': mw_amp_NV},
#        'zero_wf': {'type': 'constant', 'sample': 0.0},
#    },
#
#    'digital_waveforms': {
#        "ON": {
#            "samples": [(1, 0)]  # [(on/off, ns)]
#        },
#        "OFF": {
#            "samples": [(0, 0)]  # [(on/off, ns)]
#        }
#    },
#
#    'mixers': {
#        'mixer_qubit': [
#            {'intermediate_frequency': NV_IF_freq, 'lo_frequency': NV_LO_freq,
#             'correction': IQ_imbalance(0.40, -0.11)},  # (Amplitude, Phase) Imbalances!
#             # ok-ish for 0.2V 'correction': IQ_imbalance(0.03, -0.115)},  # (Amplitude, Phase) Imbalances!
#             # optimized  for 0.45V 'correction': IQ_imbalance(0.2, -0.148)},  # (Amplitude, Phase) Imbalances!
#             #'correction': IQ_imbalance(0.007, 0.0)},  # matched according to oscilloscope - doesnt work tho
#            #{'intermediate_frequency': NV_IF_freq, 'lo_frequency': NV_LO_freq, 'correction': IQ_imbalance(0.1, 0.1)},
#        ],
#    },
#}
#