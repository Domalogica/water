#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import config
import json


# BASE_URL = 'http://194.67.217.180:8484/'
BASE_URL = 'http://5.101.179.191:8484/'
# BASE_URL = 'http://192.168.10.30:18787/'
HOST_URL = 'host/'
DIR = 'vodomat/param'
URL = BASE_URL + DIR

STATUS = 'status'
START = 'start'
STOP = 'stop'

ERROR_METHOD = 'error'
GET_CONFIG = 'get_settings'

DEFAULD_PARAM = config.ID_DICT


def post_status(status, previous_task=None):
    return post(method=STATUS, params=status, previous_task=previous_task)


def get_config():
    response = get(GET_CONFIG)
    return response.json()


def get(method, params=DEFAULD_PARAM):
    return requests.get(url=BASE_URL + method, params=params)


def get_putting(left_score, total_paid):
    return post(method='response', params={'leftScore': left_score, 'totalPaid': total_paid})


def post(method, params=DEFAULD_PARAM, previous_task=None):
    try:
        if method == 'response':
            print(params)
        responds = requests.post(url=URL, json=build_message(method, params, previous_task))
        print(responds)
        return responds.json()
    except requests.exceptions.ConnectionError:
        return {'method': ERROR_METHOD, 'param': 'connect error'}
    except ValueError:
        return {'method': ERROR_METHOD, 'param': 'json error'}
    except ConnectionError:
        return {'method': ERROR_METHOD, 'param': 'Connection Error'}


def build_message(method, params, previous_task=None):
    return {'method': method, 'param': params, 'wm': config.ID, 'previousTask': previous_task}
