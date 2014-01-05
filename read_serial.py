__author__ = 'miahi'

## Serial logger for APC Smart UPS

import serial
import csv
import time
import datetime

PORT = 'COM2'
BAUDRATE = 2400
SLEEP_SECONDS = 3


class APCSerial(object):
    def __init__(self, port, baudrate=2400):
        # todo: check that port exists & init errors
        self.serial = serial.Serial(port, baudrate, timeout=1)
        self.serial.write('Y')
        mode = self.serial.readline()
        # todo: test init in Smart mode (UPS returns 'SM')

    def read_power(self):
        return self._read_number('P')

    def read_batt_voltage(self):
        return self._read_number('B')

    def read_temperature(self):
        return self._read_number('C')

    def read_frequency(self):
        return self._read_number('F')

    def read_line_voltage(self):
        return self._read_number('L')

    def read_max_line_voltage(self):
        return self._read_number('M')

    def read_min_line_voltage(self):
        return self._read_number('N')

    def read_output_voltage(self):
        return self._read_number('O')

    def read_batt_level(self):
        return self._read_number('f')

    def read_runtime(self):
        self.serial.write('j')
        response = self.serial.readline()
        return int(float(response.rstrip().rstrip(':')))

    def _read_number(self, command):
        self.serial.write(command)
        response = self.serial.readline()
        return float(response.rstrip())


def main():
    apcserial = APCSerial(PORT, BAUDRATE)
    filename = 'apc_log_' + time.strftime("%Y-%m-%d_%H%M%S", time.gmtime()) + '.csv'

    with open(filename, 'a+b', buffering=1) as csvfile:
        outwriter = csv.writer(csvfile, delimiter=',')
        outwriter.writerow(['Time', 'Power[%]', 'BattLevel[%]', 'BattVoltage[V]', 'LineVoltage[V]', 'MaxLineVoltage[V]',
                            'MinLineVoltage[V]', 'OutputVoltage[V]', 'Frequency[Hz]', 'EstimatedRuntime[min]',
                            'Temperature[C]'])
        while True:
            outwriter.writerow([datetime.datetime.now(), apcserial.read_power(), apcserial.read_batt_level(),
                                apcserial.read_batt_voltage(),
                                apcserial.read_line_voltage(), apcserial.read_max_line_voltage(),
                                apcserial.read_min_line_voltage(), apcserial.read_output_voltage(),
                                apcserial.read_frequency(),
                                apcserial.read_runtime(), apcserial.read_temperature()])
            csvfile.flush()
            time.sleep(SLEEP_SECONDS)


if __name__ == '__main__':
    main()