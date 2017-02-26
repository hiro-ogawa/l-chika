#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import time

wio_base_url = 'https://us.wio.seeed.io/v1/node'
led_token = ''

def clear(total_led_cnt, rgb_hex_string):
    payload = {'access_token': led_token}

    url = wio_base_url + '/GroveLedWs2812D0/clear/{total_led_cnt}/{rgb_hex_string}'.format(total_led_cnt = total_led_cnt, rgb_hex_string = rgb_hex_string)
    print(url)

    r = requests.post(url, params=payload)
    print(r)

def segment(start, rgb_hex_string):
    payload = {'access_token': led_token}

    url = wio_base_url + '/GroveLedWs2812D0/segment/{start}/{rgb_hex_string}'.format(start = start, rgb_hex_string = rgb_hex_string)
    print(url)

    r = requests.post(url, params=payload)
    print(r)

def start_rainbow_flow(length, brightness, speed):
    u""" length ledの数 1-60
    brightness 明るさ 1-100
    speed 速さ 1-10"""

    payload = {'access_token': led_token}

    url = wio_base_url + '/GroveLedWs2812D0/start_rainbow_flow/{length}/{brightness}/{speed}'.format(length = length, brightness = brightness, speed = speed)
    print(url)

    r = requests.post(url, params=payload)
    print(r)

def stop_rainbow_flow():
    payload = {'access_token': led_token}

    url = wio_base_url + '/GroveLedWs2812D0/stop_rainbow_flow'
    print(url)

    r = requests.post(url, params=payload)
    print(r)

def sleep(sleep_time_sec):
    payload = {'access_token': led_token}

    url = wio_base_url + '/pm/sleep/{sleep_time_sec}'.format(sleep_time_sec = sleep_time_sec)
    print(url)

    r = requests.post(url, params=payload)
    print(r)

def rgb2str(rgb_list):
    rgb_str = ''
    for rgb in rgb_list:
        rgb_str += '%02x' % rgb[1]
        rgb_str += '%02x' % rgb[0]
        rgb_str += '%02x' % rgb[2]
    return rgb_str

clear(50, rgb2str([[0,0,0]]))

if __name__ == "__main__":
    clear(50, rgb2str([[0,0,0]]))

    # clear test
    # if True:
    if False:
        for i in range(3):
            clear(50, rgb2str([[0,100,0]]))
            # clear(50,'ffffff')
            time.sleep(1)
            clear(50,rgb2str([[0,0,0]]))
            time.sleep(1)

    # segment test
    # if True:
    if False:
        colors = [
            rgb2str([[100,0,0]]),
            rgb2str([[0,100,0]]),
            rgb2str([[0,0,100]])
        ]
        for i in range(50):
            segment(i, colors[i%3])
        time.sleep(1)

    # if True:
    if False:

        colors = []
        for i in range(50):
            colors.append([i*3, 0, 255-i*3])
        colors_str = rgb2str(colors)

        # print colors
        # print colors_str

        segment(0, colors_str)
        time.sleep(1)

    # rainbow test
    if True:
    # if False:
        start_rainbow_flow(50, 50, 8)
        # start_rainbow_flow(50, 100, 8)
        time.sleep(5)
        stop_rainbow_flow()
        time.sleep(3)

    clear(50, rgb2str([[0,0,0]]))
