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


3. Copy config/config.default.ini to config/config.ini and add your hydro account credentials
4. Run ./hydro.py

## Available features :

- Services.getWinterCredit() to get raw winter credit data
- Services.getTodayHourlyConsumption() to get raw hourly consumption for current day
- Services.getHourlyConsumption(date = 'YYYY-MM-DD') to get hourly consumption for specific day
- Services.getDailyConsumption(start_date = 'YYYY-MM-DD',end_date = 'YYYY-MM-DD') to get a range of daily consumption
- Services.getWinterCreditEvents() to get a JSON object with past / future and next peak events

## Basic MQTT publisher

Configure the MQTT in the config file and run mqtt.py

Will publish next winter peak event to winterpeaks/next/start and winterpeaks/next/finish 

Format is YYYY-MM-DD HH:MM:SS

Feel free to tinker with it to suit your needs !

## TODO 

- What else ?
