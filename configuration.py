import numpy as np
from scipy import signal
from qualang_tools.config.integration_weights_tools import convert_integration_weights

simulate = False

# Frequencies
NV_IF_freq = 200.00e6  # in units of Hz
NV_LO_freq = 2.57e9  # in units of Hz
"""
Configuration file for the NV Center confocal setup.
"""
# Pulses lengths
laser_len = 3000  # in ns
meas_len = 600  # in ns
long_meas_len = 1e6  # in ns
odmr_meas_len = 1e6

# MW parameters
mw_amp_NV = 0.2  # in units of volts peak voltage! NOT Vpp!
mw_len_NV = 100  # in units of ns

# Gaussian pulse parameters
gauss_amp = 0.3  # The gaussian is used when calibrating pi and pi_half pulses
gauss_len_NV = 20  # The gaussian is used when calibrating pi and pi_half pulses
gauss_wf_NV = (gauss_amp * (signal.windows.gaussian(gauss_len_NV, gauss_len_NV / 5))).tolist()  # waveform

# pi parameters
pi_amp_NV = 0.1
pi_len_NV = 32

# Integration weights
optimized_weights_list = [1.0] * int(300)
optimized_weights = convert_integration_weights(optimized_weights_list)


def IQ_imbalance(g, phi):
    c = np.cos(phi)
    s = np.sin(phi)
    n = 1 / ((1 - g ** 2) * (2 * c ** 2 - 1))
    return [float(n * x) for x in [(1 - g) * c, (1 + g) * s, (1 - g) * s, (1 + g) * c]]


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
                # LO Leakage Setup for Widefield Antenna
                # 1: {'offset': 0.0152, 'delay': 73}, #75},  # NV I for OPX+ 1: {'offset': 0.0, 'delay': 0}
                # 2: {'offset': 0.002, 'delay': 73}, #75},  # NV Q

                # LO Leakage Setup for Confocal Antenna / Ist nicht schlecht als Kompromiss für beides
                # 1: {'offset': 0.0152, 'delay': 80}, #75},  # NV I for OPX+ 1: {'offset': 0.0, 'delay': 0}
                # 2: {'offset': 0.002, 'delay': 80}, #75},  # NV Q

                # LO Leakage for Confocal Antenna for 0.07 Vp OPX Config
                1: {'offset': 0.01385, 'delay': 73},  # 75},  # NV I for OPX+ 1: {'offset': 0.0, 'delay': 0}
                2: {'offset': -0.0021, 'delay': 73},  # 75},  # NV Q

                4: {'offset': 0.0},

            },
            'digital_outputs': {
                1: {},  # AOM/Laser
                # 2: {},  # Photo diode - indicator
                3: {},  # MW Trigger

            },
            'analog_inputs': {
                1: {'offset': 0},  # photo diode
                # 2: {'offset': 0},  # photo diode
            }
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
            },
        },
        'MW_Trigger': {
            'digitalInputs': {
                'marker': {
                    'port': ('con1', 3),
                    'delay': 210,
                    'buffer': 0,
                },
            },
            'operations': {
                'MW_ON': 'MW_ON',
            },
        },

        'APD': {
            "singleInput": {"port": ("con1", 4)},  # empty
            # 'digitalInputs': {
            #    'marker': {
            #        'port': ('con1', 2),
            #        'delay': 0,
            #        'buffer': 0,
            #    },
            # },
            'operations': {
                'readout_cw': 'full_readout_pulse',
                'readout': 'readout_pulse'
            },
            "outputs": {"out1": ("con1", 1)},
            'outputPulseParameters': {
                'signalThreshold': -500,  # -int(0.2/0.5*2048) - Counts arrive as NEGATIVE dips at the device
                'signalPolarity': 'Descending',
                'derivativeThreshold': 1023,
                'derivativePolarity': 'Descending'
            },
            'time_of_flight': 432,
            'smearing': 0,
        },
        'APD2': {
            "singleInput": {"port": ("con1", 4)},  # empty
            # 'digitalInputs': {
            #    'marker': {
            #        'port': ('con1', 2),
            #        'delay': 0,
            #        'buffer': 0,
            #    },
            # },
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
            'time_of_flight': 432,
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
            # 'digital_marker': 'ON',
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
            'length': pi_len_NV / 2,
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

        'MW_ON': {
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
             # IQ Imbalance for Widefield Setup
             # 'correction': IQ_imbalance(-0.0075, -0.17)},  # (Amplitude, Phase) Imbalances!

             # IQ Imbalance for Confocal Setup / Funktioniert als Kompromiss für beide Setups
             # 'correction': IQ_imbalance(-0.0075, -0.17)},  # (Amplitude, Phase) Imbalances!
             # IQ Imbalance for Confocal Setup / Funktioniert als Kompromiss für beide Setups
             # Hier liegen LO UND LO-IF >40 dBm unter LO+IF!!
             'correction': IQ_imbalance(0.40, -0.11)},  # (Amplitude, Phase) Imbalances!
        ],
    },
}
