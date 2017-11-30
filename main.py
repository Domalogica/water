#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from time import sleep

import network
import uart

# mashine = uart.Mashine(config.ID)
# mashine.start(network.get_config())
# network.post_status(mashine.get_data())


class Work(object):
    def __init__(self, device_id):
        self.mashine = uart.Mashine(device_id, debug=False)
        self.task = network.STATUS
        self.params = {}

    def run(self):
        if self.task.lower() == network.STATUS:
            self.report()
        elif self.task.lower() == network.START:
            print(self.params)
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
            print(self.task)
            self.report()


    def report(self):
            respons = network.post_status(self.mashine.get_data())
            print(respons)
            self.task = respons.get('method')
            self.params = respons.get('param')


work = Work(1)

while True:
    work.mashine.read_raw()
    work.run()
    sleep(1)
