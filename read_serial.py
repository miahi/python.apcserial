__author__ = 'miahi'

## Logger for serial APC Smart UPS

import serial
import csv
import time

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
        return int(self._parse_number(response))


    def _read_number(self, command):
        self.serial.write(command)
        response = self.serial.readline()
        return self._parse_number(response)

    @staticmethod
    def _parse_number(result):
        result = result.rstrip().rstrip(':')
        # todo: the following unrequested characters are alert messages sent by the UPS, they should be logged
        if '!' in result:  # Line Failure
            result = result.replace('!', '')
        if '$' in result:  # Power restored
            result = result.replace('$', '')
        if '%' in result:  # Low battery
            result = result.replace('%', '')
        if '+' in result:  # Return from low battery
            result = result.replace('+', '')
        if '?' in result:  # Abnormal condition
            result = result.replace('?', '')
        if '=' in result:  # Return from abnormal condition
            result = result.replace('=', '')
        if '*' in result:  # Turning off
            result = result.replace('*', '')
        if '#' in result:  # Replace battery
            result = result.replace('#', '')
        if '&' in result:  # Alarm registry
            result = result.replace('&', '')
        if '|' in result:  # EEPROM write
            result = result.replace('|', '')
        try:
            return float(result)
        except ValueError as detail:
            print "Error during parse:", result, detail
            return -1


def main():
    apcserial = APCSerial(PORT, BAUDRATE)
    filename = 'apc_log_' + time.strftime('%Y-%m-%d_%H%M%S', time.gmtime()) + '.csv'

    with open(filename, 'a+b', buffering=1) as csvfile:
        outwriter = csv.writer(csvfile, delimiter=',')
        outwriter.writerow(['Time', 'Power[%]', 'BattLevel[%]', 'BattVoltage[V]', 'LineVoltage[V]', 'MaxLineVoltage[V]',
                            'MinLineVoltage[V]', 'OutputVoltage[V]', 'Frequency[Hz]', 'EstimatedRuntime[min]',
                            'Temperature[C]'])
        while True:
            outwriter.writerow(
                [time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()), apcserial.read_power(), apcserial.read_batt_level(),
                 apcserial.read_batt_voltage(),
                 apcserial.read_line_voltage(), apcserial.read_max_line_voltage(),
                 apcserial.read_min_line_voltage(), apcserial.read_output_voltage(),
                 apcserial.read_frequency(),
                 apcserial.read_runtime(), apcserial.read_temperature()])
            csvfile.flush()
            time.sleep(SLEEP_SECONDS)


if __name__ == '__main__':
    main()