#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import sys
import json

# def ChangeBackground(file):
#     url = 'http://localhost:8082/api'
#     payload = {'background': file}
#
#     r = requests.post(url, json=payload)
#     print(r.text)
base_url = ''

def PostNewMessage(message, client_id = 'ID0001'):
    url = base_url + '/api'
    payload = {'text': message, 'clientID': client_id}

    r = requests.post(url, json=payload)
    print(r.text)

def PostNewBGM(filename, client_id = 'ID0001'):
    url = base_url + '/api/audio'
    payload = {'audio': filename, 'clientID': client_id}

    r = requests.post(url, json=payload)
    print(r.text)
