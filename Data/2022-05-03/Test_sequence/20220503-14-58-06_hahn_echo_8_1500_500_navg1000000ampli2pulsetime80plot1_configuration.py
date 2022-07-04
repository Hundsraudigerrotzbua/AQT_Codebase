import numpy as np
from scipy import signal
from qualang_tools.config.integration_weights_tools import convert_integration_weights

simulate = False

# Frequencies
NV_IF_freq = 100e6  # in units of Hz
NV_LO_freq = 2.77e9  # in units of Hz

# Pulses lengths
laser_len = 3000  # in ns
meas_len = 520 # in ns
long_meas_len = 100e3 # in ns


# MW parameters
mw_amp_NV = 0.1   # in units of volts
mw_len_NV = 80  # in units of ns

# Gaussian pulse parameters
gauss_amp = 0.3  # The gaussian is used when calibrating pi and pi_half pulses
gauss_len_NV = 20  # The gaussian is used when calibrating pi and pi_half pulses
gauss_wf_NV = (gauss_amp * (signal.windows.gaussian(gauss_len_NV, gauss_len_NV / 5))).tolist()  # waveform

# pi parameters
pi_amp_NV = 0.1
pi_len_NV = 80

# Integration weights
optimized_weights_list = [1.0] * int(300)
optimized_weights = convert_integration_weights(optimized_weights_list)


def IQ_imbalance(g, phi):
    c = np.cos(phi)
    s = np.sin(phi)
    n = 1 / ((1 - g ** 2) * (2 * c ** 2 - 1))
    return [float(n * x) for x in [(1 - g) * c,(1 + g) * s, (1 - g) * s, (1 + g) * c]]

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
                1: {'offset': 0.01385, 'delay': 73}, #75},  # NV I for OPX+ 1: {'offset': 0.0, 'delay': 0}
                2: {'offset': -0.0021, 'delay': 73}, #75},  # NV Q
                3: {'offset': 0.0},  # Nuclear spin
                4: {'offset': 0.0},

            },
            'digital_outputs': {
                1: {},  # AOM/Laser
                2: {},  # Photo diode - indicator
                3: {},  # MW Trigger

            },
            'analog_inputs': {
                1: {'offset': 0},  # photo diode
                2: {'offset': 0},  # photo diode
            }
        }
    },

    'elements': {

        'NV': {
            'mixInputs': {
                'I': ('con1', 1),
                'Q': ('con1', 2),
                #'marker': {
                #    'port': ('con1', 3),
                #    'delay': 0,
                #    'buffer': 0,
                #},
                'lo_frequency': NV_LO_freq,
                'mixer': 'mixer_qubit'
            },
            'intermediate_frequency': NV_IF_freq,
            'operations': {
                'const': 'NV_cw_pulse',
                'gauss': 'NV_gauss_pulse',
                "pi": 'NV_pi_pulse',
                "pi_half": 'NV_pi_half_pulse'
            },
        },

        'AOM': {
            'digitalInputs': {
                'marker': {
                    'port': ('con1', 1),
                    'delay': 0,
                    'buffer': 0,
                },
            },
            'operations': {
                'laser_ON': 'laser_ON',
            }
        },

        'APD': {
            "singleInput": {"port": ("con1", 4)}, # empty
            'digitalInputs': {
                'marker': {
                    'port': ('con1', 2),
                    'delay': 0,
                    'buffer': 0,
                },
            },
            'operations': {
                'readout_cw': 'full_readout_pulse',
                'readout': 'readout_pulse'
            },
            "outputs": {"out1": ("con1", 1)},
            'outputPulseParameters': {
                'signalThreshold': -500, # -int(0.2/0.5*2048) - Counts arrive as NEGATIVE dips at the device
                'signalPolarity': 'Descending',
                'derivativeThreshold': 1023,
                'derivativePolarity': 'Descending'
            },
            'time_of_flight': 420,
            'smearing': 0,
        },
        'APD2': {
            "singleInput": {"port": ("con1", 4)},  # empty
            'digitalInputs': {
                'marker': {
                    'port': ('con1', 2),
                    'delay': 0,
                    'buffer': 0,
                },
            },
            'operations': {
                'readout_cw': 'full_readout_pulse',
                'readout': 'readout_pulse'
            },
            "outputs": {"out1": ("con1", 1)},
            'outputPulseParameters': {
                'signalThreshold': -500,
                'signalPolarity': 'Descending',
                'derivativeThreshold': 1023,
                'derivativePolarity': 'Descending'
            },
            'time_of_flight': 420,
            'smearing': 0,
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
            #'digital_marker': 'ON',
        },

        'NV_gauss_pulse': {
            'operation': "control",
            'length': gauss_len_NV,
            'waveforms': {
                "I": "gauss_wf",
                "Q": "zero_wf"
            },
        },

        'NV_pi_pulse': {
            'operation': 'control',
            'length': pi_len_NV,
            'waveforms': {
                "I": "NV_pi_wf",
                "Q": "zero_wf"
            },
        },

        'NV_pi_half_pulse': {
            'operation': "control",
            'length': pi_len_NV/2,
            'waveforms': {
                "I": "NV_pi_wf",
                "Q": "zero_wf"
            },
        },

        'laser_ON': {
            'operation': 'control',
            'length': laser_len,
            'digital_marker': 'ON',
        },

        'full_readout_pulse': {
            'operation': "measurement",
            "length": long_meas_len,
            'digital_marker': 'ON',
            'waveforms': {'single': 'zero_wf'},
            "integration_weights": {"const": "long_integration_weights"},
        },
        'readout_pulse': {
            'operation': "measurement",
            "length": meas_len,
            'digital_marker': 'ON',
            'waveforms': {'single': 'zero_wf'},
            "integration_weights": {"const": "integration_weights", "optimized": "opt_integration_weights"},
        },
    },

    'waveforms': {
        'NV_const_wf': {'type': 'constant', 'sample': mw_amp_NV},
        'NV_pi_wf': {'type': 'constant', 'sample': pi_amp_NV},
        'zero_wf': {'type': 'constant', 'sample': 0.0},
        'gauss_wf': {'type': 'arbitrary', 'samples': gauss_wf_NV},
    },

    'digital_waveforms': {
        "ON": {
            "samples": [(1, 0)]  # [(on/off, ns)]
        },
        "OFF": {
            "samples": [(0, 0)]  # [(on/off, ns)]
        }
    },

    'integration_weights': {

        'integration_weights': {
            'cosine': [(1.0, meas_len)],
            'sine': [(0.0, meas_len)],
        },
        'long_integration_weights': {
            'cosine': [(1.0, long_meas_len)],
            'sine': [(0.0, long_meas_len)],
        },

    },

    'mixers': {
        'mixer_qubit': [
            {'intermediate_frequency': NV_IF_freq, 'lo_frequency': NV_LO_freq,
             'correction': IQ_imbalance(0.02, -0.11)},  # (Amplitude, Phase) Imbalances!
             # ok-ish for 0.2V 'correction': IQ_imbalance(0.03, -0.115)},  # (Amplitude, Phase) Imbalances!
             # optimized  for 0.45V 'correction': IQ_imbalance(0.2, -0.148)},  # (Amplitude, Phase) Imbalances!
             #'correction': IQ_imbalance(0.007, 0.0)},  # matched according to oscilloscope - doesnt work tho
            #{'intermediate_frequency': NV_IF_freq, 'lo_frequency': NV_LO_freq, 'correction': IQ_imbalance(0.1, 0.1)},
        ],
    },
}
