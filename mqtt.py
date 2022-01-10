#!/usr/bin/env python
"""
MQTT test publisher

This will publish only once and exit
"""

import paho.mqtt.client as paho

from config.config import Config
from winter_credit.winter_credit import WinterCredit

config = Config()
broker = config.mqtt.server
port = config.mqtt.port
user = config.mqtt.user
password = config.mqtt.password

def on_publish(client,userdata,result):             #create function for callback
    print("data published [%s]" % result)
    pass

mqtt_client= paho.Client("HydroQC")
mqtt_client.on_publish = on_publish
if user and password:
    mqtt_client.username_pw_set(username=user, password=password)
mqtt_client.connect(broker,port)
mqtt_client.loop_start()
w = WinterCredit()
next_event = w.getNextEvent()

if next_event:
    for key in next_event.keys():
        ret= mqtt_client.publish("winterpeaks/next/"+key, next_event[key], qos=1, retain=True)

state = w.getCurrentState()
if state:
    for key in state['state'].keys():
        ret = mqtt_client.publish("winterpeaks/state/" + key, state['state'][key], qos=1, retain=True)
    for topic in state['reference_period'].keys():
        for key in state['reference_period'][topic].keys():
            ret = mqtt_client.publish("winterpeaks/reference_period/%s/%s" % (topic, key), state['reference_period'][topic][key], qos=1, retain=True)

mqtt_client.loop_stop()
mqtt_client.disconnect()