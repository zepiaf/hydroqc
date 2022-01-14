#!/usr/bin/env python
"""
This code is just meant as an example / how-to use the lib

It's voluntarily very verbose :)
"""
import logging
import json
from hydro_api.services import Services
from winter_credit.winter_credit import WinterCredit

myFormatter = logging.Formatter('%(asctime)s - %(name)s [%(levelname)s] : %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(myFormatter)

logging.basicConfig(level=logging.DEBUG, handlers=[handler])
log = logging.getLogger(__name__)

def LowLevelExample():
   s = Services()
   print("WINTER CREDIT SUMMARY")
   print(json.dumps(s.getWinterCredit(), indent=True))
   print("\n\nTODAY CONSUMPTION")
   print(json.dumps(s.getTodayHourlyConsumption(), indent=True))
   print("\n\nDAILY CONSUMPTION")
   print(json.dumps(s.getDailyConsumption('2022-01-04','2022-01-05'), indent=True))


def HighLevelExample():
   w = WinterCredit()
   print (json.dumps(w.getNextEvent().to_dict()))
   print (json.dumps(w.getCurrentState(), indent=True))
   print (json.dumps(w.getFutureEvents(), indent=True))
if __name__ == "__main__":

   print ("This demo application shows how to use the low level and high level APIs")

   HighLevelExample()
