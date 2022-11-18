from qm.QuantumMachinesManager import QuantumMachinesManager
from qualang_tools.addons.calibration.calibrations import *
from configuration import *

# Relevant configuration parameters
#############################################################
resonator_element = "NV" # (required)
resonator_operation = "const" # (required)
qubit_element = "APD"         # (required)
qubit_operation = "readout"          # (required)
flux_line_element = None        # (optional)
flux_line_operation = None      # (optional)
int_w = ["const"]  # (required)
outs = ["out1"]                     # (required)
# Options for plotting figures  # (optional)
options = {
    "fontsize": 14,
    "color": "b",
    "marker": ".",
    "linewidth": 1,
    "figsize": (12, 15),
}
#############################################################

# Initialize the calibration API with the relevant configuration parameters
my_calib = QUA_calibrations(
    configuration=config,
    readout=(resonator_element, resonator_operation),
    qubit=(qubit_element, qubit_operation),
    integration_weights=int_w,
    outputs=outs,
)

# Set calibrations from the ones detailed below
scans =[
    ("duration", np.arange(16, 1000, step=50)),
    ("frequency", np.arange(2860000000, 2880000000, step=1000000))
]
my_calib.set_rabi(scan_variables=scans, iterations=100, cooldown_time=0)

# Open quantum machines manager
qmm = QuantumMachinesManager(host="192.168.1.254", port='80')

# Simulate the calibrations
my_calib.simulate_calibrations(qmm, simulation_duration=2000)

# Run the calibrations
qm = qmm.open_qm(config)
my_calib.run_calibrations(quantum_machine=qm, plot="full", plot_options=options)