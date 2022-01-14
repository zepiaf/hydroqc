#!/usr/bin/env python
"""
MQTT test publisher

This will publish only once and exit
"""

import paho.mqtt.client as paho
import datetime
import time
from config.config import Config
from winter_credit.winter_credit import WinterCredit

config = Config()
broker = config.mqtt.server
port = config.mqtt.port
user = config.mqtt.user
password = config.mqtt.password
base_topic = config.mqtt.base_topic

w = WinterCredit()
contract_id = w.api.auth.contract_id

def on_publish(client,userdata,result):             #create function for callback
    print("data published [#%s]" % result)
    pass

mqtt_client= paho.Client("HydroQC")
mqtt_client.on_publish = on_publish
if user and password:
    mqtt_client.username_pw_set(username=user, password=password)
mqtt_client.connect(broker,port)
mqtt_client.loop_start()
next_event = w.getNextEvent().to_dict()

if next_event:
    for key in next_event.keys():
        ret= mqtt_client.publish("%s/%s/winterpeaks/next/critical/%s" % (base_topic, contract_id,key), next_event[key], qos=1, retain=True)

state = w.getCurrentState()
if state:
    for key in state['state'].keys():
        ret = mqtt_client.publish("%s/%s/winterpeaks/state/%s" % (base_topic, contract_id,key), state['state'][key], qos=1, retain=True)
    for topic in state['next'].keys():
        for key in state['next'][topic].keys():
            ret = mqtt_client.publish("%s/%s/winterpeaks/next/%s/%s" % (base_topic,contract_id, topic, key), state['next'][topic][key], qos=1, retain=True)
    for topic in state['anchor_periods'].keys():
        for key in state['anchor_periods'][topic].keys():
            ret = mqtt_client.publish("%s/%s/winterpeaks/today/anchor_periods/%s/%s" % (base_topic,contract_id, topic, key), state['anchor_periods'][topic][key], qos=1, retain=True)
    for topic in state['peak_periods'].keys():
        for key in state['peak_periods'][topic].keys():
            ret = mqtt_client.publish("%s/%s/winterpeaks/today/peak_periods/%s/%s" % (base_topic,contract_id, topic, key), state['peak_periods'][topic][key], qos=1, retain=True)
    


    # Last update timestamp, should probably be in the winter_credit.py
    # TODO: Replace with proper LWT https://www.hivemq.com/blog/mqtt-essentials-part-9-last-will-and-testament/
    now = datetime.datetime.now()
    last_update = now.strftime("%Y-%m-%d %H:%M:%S")
    ret = mqtt_client.publish("%s/%s/winterpeaks/last_update" % (base_topic, contract_id), payload=last_update, qos=1, retain=True)
         
mqtt_client.loop_stop()
mqtt_client.disconnect()