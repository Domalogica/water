import zabbixactivechecks.zabbix_agent as zbx
from zabbixactivechecks import ItemList
import json
import socket
import struct
import time
from config import zabbix

# from reportBot import report


hostname = zabbix["hostname"]
server = zabbix["server"]
port = zabbix["port"]


def getkey():
    item_list = ItemList(host=hostname)
    response = item_list.get(server=server, port=port)
    return response.data


def add_data(host, key, clock, value):
    return {"host": host, "key": key, "value": value, "clock": clock}


def start_agent(row):
    while True:
        clock = int(time.time())
        request = {
            "request": "agent data",
            "data": [],
            "clock": clock
        }

        for key in row:
            try:
                if key == "ping":
                    request["data"].append(add_data(hostname, key, clock, 1))
                elif key == "leftFromPaid":
                    request["data"].append(add_data(hostname, key, clock, row[key] // 100))
                elif key == "sessionPaid":
                    request["data"].append(add_data(hostname, key, clock, row[key] // 100))
                elif key == "totalPaid":
                    request["data"].append(add_data(hostname, key, clock, row[key] // 100))
                else:
                    request["data"].append(add_data(hostname, key, clock, row[key]))

            except:
                pass
        try:
            raw = zbx.get_data_to_send(json.dumps(request))
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((server, port))
            sock.send(raw)
            data = sock.recv(5)
            if data == zbx.ZABBIX_HEADER:
                data = sock.recv(8)
                len_pack = struct.unpack("i", data[:4])[0]
                sock.recv(len_pack)
                sock.close()
        except Exception as e:
            print(e)
        time.sleep(10)

