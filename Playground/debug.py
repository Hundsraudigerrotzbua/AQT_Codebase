
# Single QUA script generated at 2022-11-29 14:17:09.039293
# QUA library version: 1.0.1

from qm.qua import *

with program() as prog:
    v1 = declare(int, )
    a1 = declare(int, size=100)
    v2 = declare(int, )
    v3 = declare(int, )
    a2 = declare(int, size=8)
    a3 = declare(int, value=[4, 104, 204, 304, 404, 504, 604, 704])
    play("laser_ON", "AOM")
    wait(100, "AOM")
    with for_(v2,0,(v2<1000),(v2+1)):
        with for_(v3,0,(v3<a2),(v3+1)):
            play("const", "NV", duration=a3[v3])
            align()
            play("laser_ON", "AOM")
            measure("readout", "APD", None, time_tagging.analog(a1, 600, v1, ""))
            assign(a2[v3], (v1+a2[v3]))
            r1 = declare_stream()
            save(a2[v3], r1)
            wait(100, )
        r2 = declare_stream()
        save(v2, r2)
    with stream_processing():
        r1.buffer(8).save("counts")
        r2.save("iteration")



    ####     SERIALIZATION VALIDATION ERROR     ####
    #
    #  Parameter to CopyFrom() must be instance of same class: expected qm.grpc.qua.QuaProgram.AnyScalarExpression got qm.grpc.qua.QuaProgram.ArrayVarRefExpression.
    #
    # Trace:
    #   ['Traceback (most recent call last):\n', '  File "D:\\Anaconda\\lib\\site-packages\\qm\\generate_qua_script.py", line 74, in _generate_qua_script_pb\n    extra_info = extra_info + _validate_program(proto_prog, serialized_program)\n', '  File "D:\\Anaconda\\lib\\site-packages\\qm\\generate_qua_script.py", line 96, in _validate_program\n    exec(serialized_program, generated_mod.__dict__)\n', '  File "<string>", line 13, in <module>\n', '  File "D:\\Anaconda\\lib\\site-packages\\qm\\qua\\_dsl.py", line 1437, in __lt__\n    return _Expression(_exp.binary(self._exp, "<", other))\n', '  File "D:\\Anaconda\\lib\\site-packages\\qm\\program\\expressions.py", line 29, in binary\n    exp.binaryOperation.right.CopyFrom(right)\n', 'TypeError: Parameter to CopyFrom() must be instance of same class: expected qm.grpc.qua.QuaProgram.AnyScalarExpression got qm.grpc.qua.QuaProgram.ArrayVarRefExpression.\n']
    #
    ################################################

            
config = {
    'version': 1,
    'controllers': {
        'con1': {
            'type': 'opx1',
            'analog_outputs': {
                '1': {
                    'offset': 0.013,
                    'delay': 80,
                },
                '2': {
                    'offset': 0.001,
                    'delay': 80,
                },
                '4': {
                    'offset': 0.0,
                },
            },
            'digital_outputs': {
                '1': {},
                '3': {},
            },
            'analog_inputs': {
                '1': {
                    'offset': 0,
                },
            },
        },
    },
    'elements': {
        'NV': {
            'mixInputs': {
                'I': ('con1', 1),
                'Q': ('con1', 2),
                'lo_frequency': 2570000000.0,
                'mixer': 'mixer_qubit',
            },
            'intermediate_frequency': 300000000.0,
            'operations': {
                'const': 'NV_cw_pulse',
                'gauss': 'NV_gauss_pulse',
                'pi': 'NV_pi_pulse',
                'pi_half': 'NV_pi_half_pulse',
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
            'singleInput': {
                'port': ('con1', 4),
            },
            'operations': {
                'readout_cw': 'full_readout_pulse',
                'readout': 'readout_pulse',
            },
            'outputs': {
                'out1': ('con1', 1),
            },
            'outputPulseParameters': {
                'signalThreshold': -500,
                'signalPolarity': 'Descending',
                'derivativeThreshold': 1023,
                'derivativePolarity': 'Descending',
            },
            'time_of_flight': 432,
            'smearing': 0,
        },
        'APD2': {
            'singleInput': {
                'port': ('con1', 4),
            },
            'operations': {
                'readout_cw': 'full_readout_pulse',
                'readout': 'readout_pulse',
            },
            'outputs': {
                'out1': ('con1', 1),
            },
            'outputPulseParameters': {
                'signalThreshold': -500,
                'signalPolarity': 'Descending',
                'derivativeThreshold': 1023,
                'derivativePolarity': 'Descending',
            },
            'time_of_flight': 432,
            'smearing': 0,
        },
    },
    'pulses': {
        'NV_cw_pulse': {
            'operation': 'control',
            'length': 100,
            'waveforms': {
                'I': 'NV_const_wf',
                'Q': 'zero_wf',
            },
        },
        'NV_gauss_pulse': {
            'operation': 'control',
            'length': 20,
            'waveforms': {
                'I': 'gauss_wf',
                'Q': 'zero_wf',
            },
        },
        'NV_pi_pulse': {
            'operation': 'control',
            'length': 32,
            'waveforms': {
                'I': 'NV_pi_wf',
                'Q': 'zero_wf',
            },
        },
        'NV_pi_half_pulse': {
            'operation': 'control',
            'length': 16.0,
            'waveforms': {
                'I': 'NV_pi_wf',
                'Q': 'zero_wf',
            },
        },
        'laser_ON': {
            'operation': 'control',
            'length': 3000,
            'digital_marker': 'ON',
        },
        'MW_ON': {
            'operation': 'control',
            'length': 3000,
            'digital_marker': 'ON',
        },
        'full_readout_pulse': {
            'operation': 'measurement',
            'length': 1000000.0,
            'digital_marker': 'ON',
            'waveforms': {
                'single': 'zero_wf',
            },
            'integration_weights': {
                'const': 'long_integration_weights',
            },
        },
        'readout_pulse': {
            'operation': 'measurement',
            'length': 600,
            'digital_marker': 'ON',
            'waveforms': {
                'single': 'zero_wf',
            },
            'integration_weights': {
                'const': 'integration_weights',
                'optimized': 'opt_integration_weights',
            },
        },
    },
    'waveforms': {
        'NV_const_wf': {
            'type': 'constant',
            'sample': 0.04,
        },
        'NV_pi_wf': {
            'type': 'constant',
            'sample': 0.1,
        },
        'zero_wf': {
            'type': 'constant',
            'sample': 0.0,
        },
        'gauss_wf': {
            'type': 'arbitrary',
            'samples': [0.017876195628595826, 0.03137370038670043, 0.05172648716812584, 0.080115550567903, 0.11656743825370923, 0.15932879731060356, 0.20458222535710444, 0.24677326871959937, 0.2796307477078583] + [0.29766538147807303] * 2 + [0.2796307477078583, 0.24677326871959937, 0.20458222535710444, 0.15932879731060356, 0.11656743825370923, 0.080115550567903, 0.05172648716812584, 0.03137370038670043, 0.017876195628595826],
        },
    },
    'digital_waveforms': {
        'ON': {
            'samples': [(1, 0)],
        },
        'OFF': {
            'samples': [(0, 0)],
        },
    },
    'integration_weights': {
        'integration_weights': {
            'cosine': [(1.0, 600)],
            'sine': [(0.0, 600)],
        },
        'long_integration_weights': {
            'cosine': [(1.0, 1000000.0)],
            'sine': [(0.0, 1000000.0)],
        },
    },
    'mixers': {
        'mixer_qubit': [{'intermediate_frequency': 300000000.0, 'lo_frequency': 2570000000.0, 'correction': [0.7275033272037215, -0.18748264467145043, -0.08034970485919304, 1.69750776347535]}],
    },
}

loaded_config = {
    'version': 1,
    'controllers': {
        'con1': {
            'type': 'opx1',
            'analog_outputs': {
                '2': {
                    'offset': 0.001,
                    'delay': 80,
                    'shareable': False,
                    'filter': {
                        'feedforward': [],
                        'feedback': [],
                    },
                },
                '4': {
                    'offset': 0.0,
                    'delay': 0,
                    'shareable': False,
                    'filter': {
                        'feedforward': [],
                        'feedback': [],
                    },
                },
                '1': {
                    'offset': 0.013,
                    'delay': 80,
                    'shareable': False,
                    'filter': {
                        'feedforward': [],
                        'feedback': [],
                    },
                },
            },
            'analog_inputs': {
                '1': {
                    'offset': 0.0,
                    'gain_db': 0,
                    'shareable': False,
                },
            },
            'digital_outputs': {
                '3': {
                    'shareable': False,
                },
                '1': {
                    'shareable': False,
                },
            },
        },
    },
    'oscillators': {},
    'elements': {
        'APD': {
            'digitalInputs': {},
            'digitalOutputs': {},
            'outputs': {
                'out1': ('con1', 1),
            },
            'time_of_flight': 432,
            'smearing': 0,
            'operations': {
                'readout_cw': 'full_readout_pulse',
                'readout': 'readout_pulse',
            },
            'singleInput': {
                'port': ('con1', 4),
            },
        },
        'APD2': {
            'digitalInputs': {},
            'digitalOutputs': {},
            'outputs': {
                'out1': ('con1', 1),
            },
            'time_of_flight': 432,
            'smearing': 0,
            'operations': {
                'readout_cw': 'full_readout_pulse',
                'readout': 'readout_pulse',
            },
            'singleInput': {
                'port': ('con1', 4),
            },
        },
        'MW_Trigger': {
            'digitalInputs': {
                'marker': {
                    'delay': 210,
                    'buffer': 0,
                    'port': ('con1', 3),
                },
            },
            'digitalOutputs': {},
            'operations': {
                'MW_ON': 'MW_ON',
            },
        },
        'AOM': {
            'digitalInputs': {
                'marker': {
                    'delay': 0,
                    'buffer': 0,
                    'port': ('con1', 1),
                },
            },
            'digitalOutputs': {},
            'operations': {
                'laser_ON': 'laser_ON',
            },
        },
        'NV': {
            'digitalInputs': {},
            'digitalOutputs': {},
            'intermediate_frequency': 300000000,
            'operations': {
                'gauss': 'NV_gauss_pulse',
                'pi_half': 'NV_pi_half_pulse',
                'const': 'NV_cw_pulse',
                'pi': 'NV_pi_pulse',
            },
            'mixInputs': {
                'I': ('con1', 1),
                'Q': ('con1', 2),
                'mixer': 'mixer_qubit',
                'lo_frequency': 2570000000,
            },
        },
    },
    'pulses': {
        'NV_pi_pulse': {
            'length': 32,
            'waveforms': {
                'Q': 'zero_wf',
                'I': 'NV_pi_wf',
            },
            'operation': 'control',
        },
        'NV_gauss_pulse': {
            'length': 20,
            'waveforms': {
                'I': 'gauss_wf',
                'Q': 'zero_wf',
            },
            'operation': 'control',
        },
        'readout_pulse': {
            'length': 600,
            'waveforms': {
                'single': 'zero_wf',
            },
            'digital_marker': 'ON',
            'integration_weights': {
                'optimized': 'opt_integration_weights',
                'const': 'integration_weights',
            },
            'operation': 'measurement',
        },
        'MW_ON': {
            'length': 3000,
            'digital_marker': 'ON',
            'operation': 'control',
        },
        'NV_pi_half_pulse': {
            'length': 16,
            'waveforms': {
                'Q': 'zero_wf',
                'I': 'NV_pi_wf',
            },
            'operation': 'control',
        },
        'full_readout_pulse': {
            'length': 1000000,
            'waveforms': {
                'single': 'zero_wf',
            },
            'digital_marker': 'ON',
            'integration_weights': {
                'const': 'long_integration_weights',
            },
            'operation': 'measurement',
        },
        'NV_cw_pulse': {
            'length': 100,
            'waveforms': {
                'I': 'NV_const_wf',
                'Q': 'zero_wf',
            },
            'operation': 'control',
        },
        'laser_ON': {
            'length': 3000,
            'digital_marker': 'ON',
            'operation': 'control',
        },
    },
    'waveforms': {
        'gauss_wf': {
            'samples': [0.017876195628595826, 0.03137370038670043, 0.05172648716812584, 0.080115550567903, 0.11656743825370923, 0.15932879731060356, 0.20458222535710444, 0.24677326871959937, 0.2796307477078583] + [0.29766538147807303] * 2 + [0.2796307477078583, 0.24677326871959937, 0.20458222535710444, 0.15932879731060356, 0.11656743825370923, 0.080115550567903, 0.05172648716812584, 0.03137370038670043, 0.017876195628595826],
            'type': 'arbitrary',
            'is_overridable': False,
            'max_allowed_error': 0.0001,
        },
        'zero_wf': {
            'sample': 0.0,
            'type': 'constant',
        },
        'NV_const_wf': {
            'sample': 0.04,
            'type': 'constant',
        },
        'NV_pi_wf': {
            'sample': 0.1,
            'type': 'constant',
        },
    },
    'digital_waveforms': {
        'OFF': {
            'samples': [(0, 0)],
        },
        'ON': {
            'samples': [(1, 0)],
        },
    },
    'integration_weights': {
        'long_integration_weights': {
            'cosine': [(1.0, 1000000)],
            'sine': [(0.0, 1000000)],
        },
        'integration_weights': {
            'cosine': [(1.0, 600)],
            'sine': [(0.0, 600)],
        },
    },
    'mixers': {
        'mixer_qubit': [{'intermediate_frequency': 300000000.0, 'lo_frequency': 2570000000.0, 'correction': [0.7275033272037215, -0.18748264467145043, -0.08034970485919304, 1.69750776347535]}],
    },
}


