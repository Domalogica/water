import serial
import json

import simulation

GET_INFO = b'g\n'
ENABLE = b'cj\n'
DISABLE = b'ci\n'
PUTTING = b'cm\n'

SETTING = 'cs'
PAYMENT = 'm'
TEXT_OUT = 'ct'
FILLTER_SET = 'cf'

NOT_ERROR = b'0\n'
ERROR_ASCII = b'-1\n'
ERROR_SHORT = b'-2\n'
ERROR_LONG = b'-3\n'
ERROR_TEST = b'-4\n'

all_keys_33 = ['input10Counter', 'out10Counter', 'milLitlose', 'milLitWentOut', 'milLitContIn', 'waterPrice',
            'containerMinVolume', 'maxContainerVolume', 'totalPaid', 'sessionPaid', 'leftFromPaid', 'totalHardCash',
            'hardCash', 'hardMoney', 'state', 'container', 'currentContainerVolume', 'consumerPump', 'mainPump',
            'magistralPressure', 'mainValve', 'filterValve', 'washFilValve', 'tumperMoney', 'tumperDoor',
            'serviceButton', 'freeButton', 'voltage', 'billAccept', 'connectBoard', 'uid_MC', 'tempCPU',
            'coffFor10LitOut']


all_keys_30 = ['input10Counter', 'out10Counter', 'milLitlose', 'milLitWentOut', 'milLitContIn', 'waterPrice',
               'containerMinVolume', 'maxContainerVolume', 'totalPaid', 'sessionPaid', 'leftFromPaid', 'state',
               'container', 'currentContainerVolume', 'consumerPump', 'mainPump', 'magistralPressure', 'mainValve',
               'filterValve', 'washFilValve', 'tumperMoney', 'tumperDoor', 'serviceButton', 'freeButton', 'voltage',
               'billAccept', 'connectBoard', 'uid_MC', 'tempCPU', 'coffFor10LitOut']


keys_data = ['input10Counter', 'out10Counter', 'milLitlose', 'milLitWentOut', 'milLitContIn', 'totalPaid',
             'sessionPaid', 'leftFromPaid', 'state', 'container', 'currentContainerVolume', 'consumerPump',
             'mainPump', 'magistralPressure', 'mainValve', 'filterValve', 'washFilValve', 'tumperMoney',
             'tumperDoor', 'serviceButton', 'freeButton', 'voltage', 'billAccept']

keys_odd = ['connectBoard', 'uid_MC', 'tempCPU', 'coffFor10LitOut']

properties_mashine = ['waterPrice', 'containerMinVolume', 'maxContainerVolume']

STATE_LIST = ['NO_WATER', 'WASH_FILTER', 'WAIT', 'JUST_PAID', 'WORK', 'SETTING', 'SERVICE', 'FREE']


agent_key = ['input10Counter', 'out10Counter', 'milLitlose', 'milLitWentOut', 'milLitContIn', 'waterPrice',
             'containerMinVolume', 'maxContainerVolume', 'totalPaid', 'sessionPaid', 'leftFromPaid', 'state',
             'container', 'currentContainerVolume', 'consumerPump', 'mainPump', 'magistralPressure', 'mainValve',
             'filterValve', 'washFilValve', 'tumperMoney', 'tumperDoor', 'serviceButton', 'freeButton', 'voltage',
             'billAccept', 'connectBoard', 'tempCPU']

# agent_additional = ['ping', ]



def raw2dict(keys, value):
    return dict(zip(keys, value))


def get_value(raw, keys):
    result = {}
    print(raw['state'])
    for key in keys:
        result.update({key: raw[key]})
    return result


class Mashine(object):
    def __init__(self, id_mashine, ports, boud, debug=False):
        self.id_mashine = id_mashine
        self.debug = debug
        if not self.debug:
            self._uart = Uart(ports, boud)
        self._all_date = {}
        self._packetInfo = {}
        self._properties = {}
        self._remainder = 0
        self._settings = {}

    def start(self, data):
        self.setting(data)
        self.read_raw()

    def zabbix(self):
        return get_value(self._all_date, agent_key)

    def get_data(self):
        self._packetInfo = get_value(self._all_date, keys_data)
        self._packetInfo['state'] = STATE_LIST[self._packetInfo['state']]
        return self._packetInfo

    def get_properties(self):
        self._properties = get_value(self._all_date, properties_mashine)
        return self._properties

    def setting(self, settings):
        self._settings = settings

    def payment(self, score):
        if not self.debug:
            self._remainder = self._uart.get_putting()
            self._uart.payment(score)
        else:
            self._remainder = score

    def get_putting(self):
        if not self.debug:
            score = self._uart.get_putting()
            self.payment(self._remainder)
            self.read_raw()
            return score
        else:
            score = self._remainder
            self._remainder = 0
            return score

    def read_raw(self):
        if not self.debug:
            raw = self._uart.read_info()
            try:
                print('raw -> %s len %i' % (raw, len(raw)))
            except TypeError:
                print('raw -> %s len 0' % raw)
            json_raw = json.loads(raw.decode())
            if len(json_raw) == 30:
                self._all_date = raw2dict(all_keys_30, json_raw)
            elif len(json_raw) == 33:
                self._all_date = raw2dict(all_keys_33, json_raw)
        else:
            raw = simulation.all_date
            self._all_date = raw2dict(all_keys_30, raw)
        return self._all_date

    def __del__(self):
        try:
            self._uart.close()
        except AttributeError:
            pass


def check_code(code, types='code'):
    if types == 'code':
        if code == NOT_ERROR:
            return True
        else:
            return False
    elif types == 'int':
        if int(code) >= 0:
            return int(code)
        else:
            return -1


class Uart(object):
    def __init__(self, port='com5', boud_rate=9600):
        self.serial = serial.Serial(port, boud_rate, timeout=1)

    def get_putting(self):
        self.write(PUTTING)
        result = check_code(self.read(), types='int')
        i = 0
        while result < 0 and i < 3:
            i += 1
            result = check_code(self.read(), types='int')
        return result

    def payment(self, score):
        data = "%s%i\n" % (PAYMENT, score)
        self.write(data.encode('ascii'))
        return self.read_code()

    def read_info(self):
        self.write(GET_INFO)
        if self.read_code():
            return self.read()

    def enable_payment(self):
        self.write(ENABLE)
        return self.read_code()

    def disable_payment(self):
        self.write(DISABLE)
        return self.read_code()

    def read_code(self):
        if check_code(self.read()):
            return True
        else:
            return False

    def write(self, data):
        return self.serial.write(data)

    def read(self):
        return self.serial.readline()

    def close(self):
        self.serial.close()

    def __del__(self):
        self.close()
