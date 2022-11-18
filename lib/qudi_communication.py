import jupyter_client as jc
import time


def run_kernel_command(cmd='optimizerlogic.start_refocus(scannerlogic.get_position(), "confocalgui")', wait=20):
    """
    Dirty workaround for QUDIs Jupyter Kernel Interaction to automize QUDI control.
    :param cmd: Command to be played via the Jupyter Kernel.
    :param wait: Waiting time to finish the execution. (Is this automizable maybe?)
    """
    # find the absolute path of the most recent jupyter kernel connection file
    conn_file = jc.find_connection_file()

    # prepare kernel manager
    km = jc.KernelManager(connection_file=conn_file)

    # establish connection to kernel
    km.load_connection_file()

    km.client().execute(cmd)

    time.sleep(wait)
    # execute command in kernel
    #km.client().execute(cmd)

    # shut down connection
    #km.client().shutdown()
