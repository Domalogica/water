#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from time import sleep
import os
import threading

import network
import uart
import agent
import gpio

# mashine = uart.Mashine(config.ID)
# mashine.start(network.get_config())
# network.post_status(mashine.get_data())


class Work(object):
    def __init__(self, device_id, ports, boud):
        self.mashine = uart.Mashine(device_id, ports, boud, debug=False)
        self.task = network.STATUS
        self.params = {}

    def run(self):
        if self.task.lower() == network.STATUS:
            self.report()
        elif self.task.lower() == network.START:
            self.mashine.payment(self.params.get('score', 0))
            self.report()
        elif self.task.lower() == network.STOP:
            response = network.get_putting(self.mashine.get_putting(), self.mashine.get_data()['totalPaid'])
            self.task = response.get('method')
            self.params = response.get('param')
        elif self.task == network.ERROR_METHOD:
            self.task = 'normalise'
            print(self.task, self.params)
            self.report()
        else:
            self.report()

    def report(self):
            response = network.post_status(self.mashine.get_data())
            self.task = response.get('method')
            self.params = response.get('param')


if os.name == 'nt':
    work = Work(1, 'com5', 9600)
else:
    work = Work(1, '/dev/ttyS1', 9600)

gpio.init()

agent_thread = threading.Thread(target=agent.start_agent)
agent_thread.start()

while True:
    work.mashine.read_raw()
    work.run()
    agent.load_data(work.mashine.zabbix())
    sleep(1)
