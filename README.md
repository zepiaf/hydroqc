# HydroQC
Hydro Quebec API wrapper.

This is a package to access some functionalities of Hydro Quebec API that are not documented.

We started a discord server for the project where you can come to discuss or find help with the project : https://discord.gg/BTPDntfaXH

## Documentation

### Code documentation
[https://hydroqc.readthedocs.io/](https://hydroqc.readthedocs.io/)

### Architecture / concepts
If you need more information about the winter credit, the associated terms, documents, ... :
   [Winter Credit lexicon and concepts](https://hydroqc.readthedocs.io/en/latest/wintercredit/wintercredit.html)

## Credit

Thibault Cohen who wrote [pyhydroquebec](https://github.com/titilambert/pyhydroquebec/) 
That's where I took most of the inspiration (and some portions of the code)

## Goal

Make it easy to fetch and manipulate data from hydro quebec, especially the winter credit periods

## How-to
This uses python 3 (tested with 3.8)

1. clone the repo
2. create a virtual-env

    $ python -m venv hydro-env

    $ . hydro-env/bin/activate

    (hydro-env) $ pip install -r requirements.txt


3. Copy config/config.default.yaml to config/config.yaml and add your hydro account credentials
4. Run ./hydro.py

## Available features :

- Services.getWinterCredit() to get raw winter credit data
- Services.getTodayHourlyConsumption() to get raw hourly consumption for current day
- Services.getHourlyConsumption(date = 'YYYY-MM-DD') to get hourly consumption for specific day
- Services.getDailyConsumption(start_date = 'YYYY-MM-DD',end_date = 'YYYY-MM-DD') to get a range of daily consumption
- WinterCredit.getFutureEvents() to get a list of JSON object with future peak events
```
[
 {
  "date": "2022-01-11",
  "start": "2022-01-11 16:00:00",
  "end": "2022-01-11 20:00:00",
  "start_ts": 1641934800.0,
  "end_ts": 1641949200.0,
  "pre_heat_start": "2022-01-11 13:00:00",
  "pre_heat_end": "2022-01-11 16:00:00",
  "pre_heat_start_ts": 1641924000.0,
  "pre_heat_end_ts": 1641934800.0
 },
 {
  "date": "2022-01-11",
  "start": "2022-01-11 06:00:00",
  "end": "2022-01-11 09:00:00",
  "start_ts": 1641898800.0,
  "end_ts": 1641909600.0,
  "pre_heat_start": "2022-01-11 03:00:00",
  "pre_heat_end": "2022-01-11 06:00:00",
  "pre_heat_start_ts": 1641888000.0,
  "pre_heat_end_ts": 1641898800.0
 },
 {
  "date": "2022-01-10",
  "start": "2022-01-10 16:00:00",
  "end": "2022-01-10 20:00:00",
  "start_ts": 1641848400.0,
  "end_ts": 1641862800.0,
  "pre_heat_start": "2022-01-10 13:00:00",
  "pre_heat_end": "2022-01-10 16:00:00",
  "pre_heat_start_ts": 1641837600.0,
  "pre_heat_end_ts": 1641848400.0
 }
]

```
- WinterCredit.getNextEvent() to get the next event :
```
{
 "date": "2022-01-10",
 "start": "2022-01-10 16:00:00",
 "end": "2022-01-10 20:00:00",
 "start_ts": 1641848400.0,
 "end_ts": 1641862800.0,
 "pre_heat_start": "2022-01-10 13:00:00",
 "pre_heat_end": "2022-01-10 16:00:00",
 "pre_heat_start_ts": 1641837600.0,
 "pre_heat_end_ts": 1641848400.0
}
```
- WinterCredit.getState() to get current information like :
```
{
 "state": {
  "current_period": "normal", # peak | normal | anchor : what kind of period is happening now (at the moment this script run)
  "current_period_time_of_day": # peak_morning | peak_evening | anchor_morning | anchor_evening | normal : like the above but combined with the time of day
  "peak_critical": true # true | false : is the next peak period a critical peak
  "upcoming_event": true # true | false : is there an critical peak event announced by HQ, not matter when it is happening.
  "event_in_progress": false, # true | false : if there is currently a critical peak event in progress
  "pre_heat": true, # true | false : if we are currently in a pre-heat period as defined in the config
  "morning_event_today": false, # true | false : Is there a critical peak event in the morning today
  "evening_event_today": true, # true | false : Is there a critical peak event in the evening today
  "morning_event_tomorrow": true, # true | false : Is there a critical peak event in the morning tomorrow
  "evening_event_tomorrow": true # true | false : Is there a critical peak event in the evening tomorrow
 },
 "reference_period": {
  "morning": {
   "date": "2022-01-10",
   "start": "2022-01-10 01:00:00",
   "end": "2022-01-10 04:00:00",
   "start_ts": 1641794400.0,
   "end_ts": 1641805200.0
  },
  "evening": {
   "date": "2022-01-10",
   "start": "2022-01-10 11:00:00",
   "end": "2022-01-10 14:00:00",
   "start_ts": 1641830400.0,
   "end_ts": 1641841200.0
  }
 }
}

```
## Basic MQTT publisher

Configure the MQTT in the config file and run mqtt.py

Will publish next winter peak event and current status to the winterpeaks topic
winterpeaks/next -> next event
winterpeaks/state -> current state
winterpeaks/reference_periods -> reference periods for the current day

datetime format is YYYY-MM-DD HH:MM:SS (can be configured) and {field}_ts is unix epoch

Feel free to tinker with it to suit your needs !

## NOTES

As per issue https://github.com/zepiaf/hydroqc/issues/11 the certificate chain for service.hydroquebec.com is not 
downloaded correctly. It has been forced in the code. It will not be used if verification is disabled.

## TODO 
- Describe the different values returned
- What else ?
