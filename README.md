# Nagy Lab Data Structure
### File System
Traceability of measurements has to be ensured. For this reason every measurement must include an automatic and structured saving of the produced data. Regardless of the systems state.

The Data Structure of all collected measurements is as follows:
- [Data] Directory
    * YEAR
        * MONTH
            * YEARMONTHDAY
              * EXPERIMENTID_YEARMONTHDAY_HOUR-MINUTE-SECOND_scheme__EXPERIMENTTAG

Each time an experiment is run, a new directory will be created. This contains all data, settings and created plots for
the specified experiment run:


    - Raw Data as .npz: MEASUREMENTID_OPTIMIZERITERATION_TIMESTAMP_SCHEME__EXPERIMENTTAG.npz
    - Optimizer Image data as .npz: refocus_OPTIMIERITERATION_TIMESTAMP.npz
    - Hardware Settings .json File including all Settings to reproduce the measurement reliably:
        - Experiment Settings
        - Laser Power (mW)
        - Laser power measurement location
        - Emissionfilter used
        - OPX Config File used
        - Measurement Sequences File used
        - Measurement Script used

This Data Structure is organized via the data_handler.py and plot_lib.py libraries.

### Code Base

The code base should be kept in an organized structure, so that multiple users can work independently without affecting
the productivity of each other.

For this reason the shared module library "lib" is the only directory that is shared between the labs.

The directory "Playground" and "Measurements" contain setup specific try-outs or working measurement schemes. The
scripted experiments explained farther below will be located in the Measurements/ directory.

The setup specific config files are saved in the base directory of the project.

DO NOT CREATE UNNECESSARY OR REDUNDANT CONFIG FILES!

####git ignore

It is important to implement a git ignore statement for all data that is measured. The only files that should be shared
and comitted are the library files! No data should be left in the git repository, it should only be stored local!

```
.
├── 🗀 .git/
├── 🗀 Measurements/
│   ├── __init__.py
│   ├── cw-odmr.py
│   └── time_rabi.py
├── 🗀 Playground/
│   └── stuff-that-isnt-fixed-and-reviewed-yet.py
├── 🗀 lib/
│   ├── 🗀 widefield_lib/.py
│   ├── __init__.py
│   ├── data_handler.py
│   ├── plot_lib.py
│   └── sequences.py
├── .gitignore
├── configuration.py
└── configuration_widefield.py
```
### Experiment Setup
An example of an experiment run in the established data structure is as follows:

    """
    A rabi experiment sweeping the time of the microwave pulse.
    """
    from lib.sequences import *
    from lib.data_handler import *

    my_settings = {
    't_min': 16,  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
    't_max': 800,  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
    'dt': 40,  # in ns, will be converted to clock cycles in the sequence (must be >= 16)
    'n_avg': 2.5e6,
    #'optimizer_interval': 180, # duration of one measurement in seconds
    # Dauer bis Optimizer: len(np.arange(t_min, t_max, dt))*3.5e-6 * n_avg (3.5e-6 ist ungefähre Dauer für Laser + Warten)
    'Laser power (mW)': 0.6,
    'Laser power measured at': 'Infront of dichroic mirror',
    'emission_filter': 'BasicEdge',
    }
    my_settings.update(
    {'t_vec': np.arange(my_settings['t_min'] // 4, my_settings['t_max'] // 4 + 0.1, my_settings['dt'] // 4).tolist()})

    scheme = 'rabi'
    measurement_tag = f'leipzig_sample_rabi_test_after_repositioning_antenna'
    work_dir = set_up_measurement(scheme, measurement_tag=measurement_tag, settings_file='hardwarefile',
    settings=my_settings, script_path=__file__)

    measurement_ID = generate_measurement_id(work_dir)
    qmm, qm = setup_qm()
    simulate = False
    counts = np.zeros(len(my_settings['t_vec']), dtype=np.int64)
    fig, ax = plt.subplots(1, 1)
    iteration = 0
    i = 0
    while 1:
    refocus(qm, iteration=i, path=work_dir)
    counts, iteration = time_rabi(qmm, qm, fig,
    #frequency=300.0e6,
    settings=my_settings,
    prev_counts=counts,
    prev_iterations=iteration,
    ax=ax)
    save_data(work_dir, scheme, measurement_tag,
    file_id=measurement_ID,
    optimizer_iteration=i,
    times=my_settings['t_vec'],
    counts=counts,
    iterations=iteration)
    save_pdf(scheme, work_dir, measurement_tag, my_settings['t_vec'], counts,
    file_id=measurement_ID,
    optimizer_iteration=i)
    i += 1
    # execute QUA program
    qm.close()

The experiment settings are specified in the my_settings dictionary and will be handed to the data_handler to store in the
experiment directory.

The scheme and experiment description are specified in "scheme" and "file_tag".

A working directory is created for the experiment run.

A Quantum Machines Manager Instance is generated and all running OPX Jobs, containing ports that will be used for the
experiment to follow, are closed.

Some experiment specific setups follow.

A measurement_ID is generated for this particular instance before the while loop, since no parameters are being swept in
this case. If one was to modify a parameter programmatically, each iteration should be assigned a measurement_ID.

Inside the while loop a optimizer refocus is performed and the corresponding Optimizer image is saved. 

Afterwards the actual measurement job is executed.

Finally saving of both the data and the plots as .pdf is performed.

The Quantum Machine is closed.

### This is a WIP document and the actual measurement execution might change in the future.
### A. Pointner, 01.2023
#### PS: Dont forget to sign everything into the lab book!
#### PPS: LEARN GIT! >:(



### TODO: Labbook Integration
In order to improve the usability and reproducability of the measurements the Microsoft Office365 REST API will be used to additionally save all measurements automatically to the Quantech Labbook. WIP.
