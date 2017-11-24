#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from time import sleep
import requests

import network
import uart
import config

# mashine = uart.Mashine(config.ID)
# mashine.start(network.get_config())
# network.post_status(mashine.get_data())


class Work(object):
    def __init__(self, device_id):
        self.mashine = uart.Mashine(device_id)
        self.task = network.STATUS
        self.params = {}

    def report(self):
        if self.task == network.STATUS:
            respons = network.post_status(self.mashine.get_data())
            print(respons)
            self.task = respons.get('method')
            self.params = respons.get('param')
        elif self.task == network.ERROR_METHOD:
            print()


work = Work(1)

while True:
    work.mashine.read_raw()
    work.report()
    sleep(1)
