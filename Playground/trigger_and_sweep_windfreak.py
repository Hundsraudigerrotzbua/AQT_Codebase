import pyvisa as visa


class OPX_MW:
    serial_port = 'COM3'
    serial_timeout = 10

    def activate(self):
        self.rm = visa.ResourceManager()
        self._conn = self.rm.open_resource(
            self.serial_port,
            baud_rate=9600,
            read_termination='\n',
            write_termination='\n',
            timeout=self.serial_timeout * 1000
        )
        self.model = self._conn.query('+')  # Modellnumber
        self.sernr = self._conn.query('-')  # Serialnumber
        self.mod_hw = self._conn.query('v1')  # Hardware version
        self.mod_fw = self._conn.query('v0')  # Software version
        self.t = self._conn.query('z')  # Temperature in C 27.750 (?)

    def deactivate(self):
        """ Deinitialisation performed during deactivation of the module.
        """
        self._conn.close()
        self.rm.close()

    def off(self):
        self._conn.write('g0')
        self._conn.write('y0')
        print(self._off())
        return 0

    def _off(self):
        self._conn.write('E0h0')
        return self._stat()

    def _on(self):
        self._conn.write('E1h1')
        return self._stat()

    def _stat(self):
        E = int(self._conn.query('E?'))
        h = int(self._conn.query('h?'))
        return E, h

    def cw_on(self):
        self._on()
        self._conn.write('g1')

    def set_cw(self, frequency=None, power=None):
        """
        Configures the device for cw-mode and optionally sets frequency and/or power

        @param float frequency: frequency to set in Hz
        @param float power: power to set in dBm
        @return float, float, str: current frequency in Hz, current power in dBm, current mode
        """

        self._conn.write('X0')
        self._conn.write('c1')

        # trigger mode: software
        self._conn.write('y0')

        # sweep frequency and steps

        if frequency is not None:
            self._conn.write('f{0:5.7f}'.format(frequency / 1e6))
            self._conn.write('l{0:5.7f}'.format(frequency / 1e6))
            self._conn.write('u{0:5.7f}'.format(frequency / 1e6))
        if power is not None:
            self._conn.write('W{0:2.3f}'.format(power))
            self._conn.write('[{0:2.3f}'.format(power))
            self._conn.write(']{0:2.3f}'.format(power))

        self.mw_cw_freq = float(self._conn.query('f?')) * 1e6
        self.mw_cw_power = float(self._conn.query('W?'))
        return self.mw_cw_freq, self.mw_cw_power, 'cw'

    def sweep_on(self):
        """ Switches on the sweep mode.

        @return int: error code (0:OK, -1:error)
        """
        self._on()
        # enable sweep mode and set to start frequency
        self._conn.write('g1')
        # query sweep mode
        mode = int(self._conn.query('g?'))
        return 0

    def set_sweep(self, start=None, stop=None, step=None, power=None):
        """
        Configures the device for sweep-mode and optionally sets frequency start/stop/step
        and/or power

        @return float, float, float, float, str: current start frequency in Hz,
                                                 current stop frequency in Hz,
                                                 current frequency step in Hz,
                                                 current power in dBm,
                                                 current mode
        """
        if (start is not None) and (stop is not None) and (step is not None):
            # sweep mode: linear sweep, non-continuous
            self._conn.write('X0')
            self._conn.write('c1')

            # trigger mode: single step
            self._conn.write('y2')
            self._conn.write('t37.5')

            # sweep direction
            if stop >= start:
                self._conn.write('^1')
            else:
                self._conn.write('^0')

            # sweep lower and upper frequency and steps
            self._conn.write('l{0:5.7f}'.format(start / 1e6))
            self._conn.write('u{0:5.7f}'.format(stop / 1e6))
            self._conn.write('s{0:5.7f}'.format(step / 1e6))

        # sweep power
        if power is not None:
            # set power
            self._conn.write('W{0:2.3f}'.format(power))
            # set sweep lower end power
            self._conn.write('[{0:2.3f}'.format(power))
            # set sweep upper end power
            self._conn.write(']{0:2.3f}'.format(power))

        # query lower frequency
        mw_start_freq = float(self._conn.query('l?')) * 1e6
        # query upper frequency
        mw_stop_freq = float(self._conn.query('u?')) * 1e6
        # query sweep step size
        mw_step_freq = float(self._conn.query('s?')) * 1e6
        # query power
        mw_power = float(self._conn.query('W?'))
        # query sweep lower end power
        mw_sweep_power_start = float(self._conn.query('[?'))
        # query sweep upper end power
        mw_sweep_power_stop = float(self._conn.query(']?'))
        return (
            mw_start_freq,
            mw_stop_freq,
            mw_step_freq,
            mw_sweep_power_start,
            'sweep'
        )

    def reset_sweeppos(self):
        """
        Reset of MW sweep mode position to start (start frequency)

        @return int: error code (0:OK, -1:error)
        """
        # enable sweep mode and set to start frequency
        self._conn.write('g1')
        return 0

    def set_ext_trigger(self,dwelltime):
        """ Set the external trigger for this device with proper polarization.

        @param TriggerEdge pol: polarisation of the trigger (basically rising edge or falling edge)
        @param dwelltime: minimum dwell time

        @return object: current trigger polarity [TriggerEdge.RISING, TriggerEdge.FALLING]
        """
        self._conn.write('t{0:f}'.format(0.75 * dwelltime))
        newtime = float(self._conn.query('t?'))
        return newtime

    def trigger(self):
        """ Trigger the next element in the list or sweep mode programmatically.

        @return int: error code (0:OK, -1:error)

        Ensure that the Frequency was set AFTER the function returns, or give
        the function at least a save waiting time.
        """
        return

if __name__ == '__main__':
    MW = OPX_MW()
    MW.activate()
    MW.set_cw(frequency=2870000000, power=-30)
    MW.cw_on()
