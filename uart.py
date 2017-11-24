import serial
import json
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

keys_data = ['input10Counter', 'out10Counter', 'milLitlose', 'milLitWentOut', 'milLitContIn', 'totalPaid',
             'sessionPaid', 'leftFromPaid', 'state', 'container', 'currentContainerVolume', 'consumerPump',
             'mainPump', 'magistralPressure', 'mainValve', 'filterValve', 'washFilValve', 'tumperMoney',
             'tumperDoor', 'serviceButton', 'freeButton', 'voltage', 'billAccept']

d = [0, 0, 0, 0, 0, 0, 0, 0, 'WAIT', 'TOO_LOW', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

keys_odd = ['connectBoard', 'uid_MC', 'tempCPU', 'coffFor10LitOut']

properties_mashine = ['waterPrice', 'containerMinVolume', 'maxContainerVolume']

all_keys = ['input10Counter', 'out10Counter', 'milLitlose', 'milLitWentOut', 'milLitContIn', 'waterPrice',
            'containerMinVolume', 'maxContainerVolume', 'totalPaid', 'sessionPaid', 'leftFromPaid', 'state',
            'container', 'currentContainerVolume', 'consumerPump', 'mainPump', 'magistralPressure', 'mainValve',
            'filterValve', 'washFilValve', 'tumperMoney', 'tumperDoor', 'serviceButton', 'freeButton', 'voltage',
            'billAccept', 'connectBoard', 'uid_MC', 'tempCPU', 'coffFor10LitOut']


all_date = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'WAIT', 'TOO_LOW', 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 3000, 0, 1, '0x324343223452365', 23, 5000]


def raw2dict(keys, value):
    return dict(zip(keys, value))


def get_value(raw, keys):
    result = {}
    for key in keys:
        result.update({key: raw[key]})
    return result


class Mashine(object):
    def __init__(self, id_mashine):
        self.id_mashine = id_mashine
        self._uart = Uart()
        self._all_date = {}
        self._packetInfo = {}
        self._properties = {}
        self._remainder = 0
        self._settings = {}

    def start(self, data):
        self.setting(data)
        self.read_raw()

    def get_data(self):
        self._packetInfo = get_value(self._all_date, keys_data)
        return self._packetInfo

    def get_properties(self):
        self._properties = get_value(self._all_date, properties_mashine)
        return self._properties

    def setting(self, settings):
        self._settings = settings

    def payment(self, score):
        self._remainder = self._uart.get_putting()
        self._uart.payment(score)

    def get_putting(self):
        score = self._uart.get_putting()
        self.payment(self._remainder)
        return score

    def read_raw(self):
        raw = self._uart.read_info()
        self._all_date = raw2dict(all_keys, json.loads(raw.decode()))
        return self._all_date

    def __del__(self):
        self._uart.close()


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
            raise IOError


class Uart(object):
    def __init__(self, port='com15', boud_rate=9600):
        self.serial = serial.Serial(port, boud_rate, timeout=1)

    def get_putting(self):
        self.write(PUTTING)
        return check_code(self.read_code(), types='int')

    def payment(self, score):
        data = "%s%i\n" % (PAYMENT, score)
        self.write(data.encode('ascii'))
        return self.read_code()

    def read_info(self):
        self.write(GET_INFO)
        readed = self.read_code()
        if readed:
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
            raise IOError

    def write(self, data):
        print('write -> %s' % data)
        return self.serial.write(data)

    def read(self):
        date = self.serial.readline()
        print('read -> %s' % date)
        print(date)
        return date

    def close(self):
        self.serial.close()

    def __del__(self):
        self.close()
