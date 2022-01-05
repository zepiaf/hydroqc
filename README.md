# HydroQC
Hydro Quebec API wrapper.

This is a package to access some functionalities of Hydro Quebec API that are not documented.

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

3. Copy config/config.default.ini and add your hydro account credentials
4. Run ./hydro.qc

## TODO 

- Parse output and send to homeassistant (mqtt ??)
- What else ?