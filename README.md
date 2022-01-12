# HydroQC
Hydro Quebec API wrapper.

This is a package to access some functionalities of Hydro Quebec API that are not documented.

## Documentation

[https://hydroqc.readthedocs.io/](https://hydroqc.readthedocs.io/)

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
  "current_state": "normal",
  "event_in_progress": false,
  "pre_heat": true,
  "morning_event_today": false,
  "evening_event_today": true,
  "morning_event_tomorrow": true,
  "evening_event_tomorrow": true
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

# Lexicon


The following are the terms in use in this module and coming as much as possible from the official Hydro-Quebec electricy rates document (page 31)
https://www.hydroquebec.com/data/documents-donnees/pdf/electricity-rates.pdf

and from the "Regie de l'énergie" document http://publicsde.regie-energie.qc.ca/projets/469/DocPrj/R-4057-2018-B-0062-DDR-RepDDR-2018_10_26.pdf#page=124

## Period

A period is time window where a specific billing or algorythmic logic is applied by HQ

### normal
A period when nothing special is defined by HQ rate policies

### peak (peak hours)

In this module: All hours from 06:00 to 09:00 and from 16:00 to 20:00 during the winter.

This is when the critical peak events from hydro are happening. 

In hydro's document there are also exclusions for specific holiday dates (Christmans, New year, Good Friday and Easter Monday) that we don't take into account here (yet)

### anchor (temperature adjustement)

This period starts 5 hours before the next peak event's start time and has a duration of 3 hours. With the current peak period (as described above) it results in the following time periods: 

**Morning**
01h00-04h00

**Evening**
11h00-14h00

This period is used by HQ in combination with the reference period to calculate the Reference Energy used to calculate the credit by trying to guess the additionnal energy usage caused by the colder temperature.

In HQ's rate document it is called temperature adjustment and in the "Regie de l'énergie" docuement it is refered to as an "anchor" period.

### reference period

This value is not used or provided in winter_module.py but is good to know about to give some context to the calculations.

The period corresponding to the last 5 non-critical event, differenciated by weekend vs week days.

Saturday evening critical peak  event's reference period = Last 5 non-critical evening peaks that occured on weekend days

Wednesday morning critical peak event's reference period = Last 5 non-critical morning peaks that occurend on week days


## event (critical peak event)

An event is also refered to a "critical peak event" means that HQ sent a notification that the peak period will be considered critical and admissible to winter credits

### critical

When a period is critical it can means two things depending on the period type:

#### peak period
The current peak period is part of a "critical peak event"

#### normal period or anchor period
Means that the next immediate peak period will be a "critical peak event"

### none (or normal/regular?)
The period is not or will not be critical.

## pre-heat (pre-peak or pre-critical-preak?)

A period of time when we want to run some automations before a critical peak event's start. Ex: raise the thermostat setpoint.


## TODO 
- Describe the different values returned
- What else ?
