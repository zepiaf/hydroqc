#!/usr/bin/env python
"""
MQTT test publisher

This will publish only once and exit
"""

import paho.mqtt.client as paho
import configparser
from hydro_api.services import Services

config = configparser.ConfigParser()
config.read('config/config.ini')

broker = config.get('MQTT', 'server')
port = config.getint('MQTT', 'port')
user = config.get('MQTT', 'user')
password = config.get('MQTT', 'password')

mqtt_client= paho.Client("HydroQC")
if user and password:
    mqtt_client.username_pw_set(username=user, password=password)
mqtt_client.connect(broker,port)

s = Services()
events = s.getWinterCreditEvents()

if 'next' in events:
    for e in events['next']:
        ret= mqtt_client.publish("winterpeaks/next/start", "%s %s" % (events['next'][e]['date'], events['next'][e]['start']), qos=1, retain=True)
        ret= mqtt_client.publish("winterpeaks/next/finish", "%s %s" % (events['next'][e]['date'], events['next'][e]['end']), qos=1, retain=True)
        ret= mqtt_client.publish("winterpeaks/next/pre_start", events['next'][e]['pre_start'], qos=1, retain=True)
