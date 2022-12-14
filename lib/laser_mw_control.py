from lib.sequences import *
from qm.qua import *

################################################
###### Script to toggle laser / microwave  #####
################################################
def run():
    qmm, qm = setup_qm()

    with program() as counter:
        with infinite_loop_():
            play('laser_ON', 'AOM', duration=int(3000 // 4))
            play('const', 'NV', duration=int(3000// 4))  # play microwave pulse

    job = qm.execute(counter)
    try:
        pass
    except KeyboardInterrupt:
        job.halt()
        qm.close()


if __name__ == '__main__':
    run()
