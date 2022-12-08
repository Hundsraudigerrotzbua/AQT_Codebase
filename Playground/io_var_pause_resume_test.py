import time
from lib.sequences import *
with program() as prog:
    N= declare(int)
    a=declare(fixed)
    a_st = declare_stream()
    with for_(N, 0, N<100, N+1):
        pause()
        assign(a, IO1)
        save(a, a_st)

qmm, qm = setup_qm()

job = qm.execute(prog)
current_vals = np.linspace(1e-3, 5e-3, 100)
for val in current_vals:
    while not job.is_paused():
        print('wait')
        time.sleep(0.001)
    print('Setting value')
    qm.set_io1_value(val)
    job.resume()