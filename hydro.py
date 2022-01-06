#!/usr/bin/env python
"""
This code is just meant as an example / how-to use the lib

It's voluntarily very verbose :)
"""
import logging
import json
from hydro_api.services import Services

myFormatter = logging.Formatter('%(asctime)s - %(name)s [%(levelname)s] : %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(myFormatter)

logging.basicConfig(level=logging.DEBUG, handlers=[handler])
log = logging.getLogger(__name__)

if __name__ == "__main__":
   s = Services()
   print(json.dumps(s.getWinterCredit(), indent=True))
   print(json.dumps(s.getTodayHourlyConsumption(), indent=True))
   print(json.dumps(s.getDailyConsumption('2022-01-04','2022-01-05'), indent=True))
   print (json.dumps(s.getWinterCreditEvents(reference_datetime='2022-01-04 10:00:00'), indent=True))
