import logging
import json

import datetime

from dateutil import parser
from .auth import Hydro

log = logging.getLogger(__name__)

class Services:
    def __init__(self):
        self.auth = Hydro()
        self.auth.login()
        self.api_headers = self.auth.get_api_headers()
        self.session = self.auth.session

    def getWinterCredit(self):
        """Return information about the winter credit

        :return: raw JSON from hydro QC API
        """
        API_URL = "https://cl-services.idp.hydroquebec.com/cl/prive/api/v3_0/tarificationDynamique/creditPointeCritique"
        params = {
            'noContrat': self.auth.contract_id
        }
        api_call_response = self.session.get(API_URL, headers=self.api_headers, params=params,
                                             verify=self.auth.config.getboolean('Global', 'validate_ssl'))
        return json.loads(api_call_response.text)

    def getTodayHourlyConsumption(self):
        """Return latest consumption info (about 2h delay it seems)

        :return: raw JSON from hydro QC API for current day (not officially supported, data delayed)
        """
        date = datetime.date
        today = date.today().strftime('%Y-%m-%d')
        yesterday = (date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        # We need to call a valid date first as theoretically today is invalid
        # and the api will not respond if called directly
        self.getHourlyConsumption(yesterday)
        return self.getHourlyConsumption(today)

    def getHourlyConsumption(self, date):
        """Return hourly consumption for a specific day

        :param: date: YYYY-MM-DD string to pass to API

        :return: raw JSON from hydro QC API
        """
        API_URL = 'https://cl-ec-spring.hydroquebec.com/portail/fr/group/clientele/portrait-de-consommation' \
                  '/resourceObtenirDonneesConsommationHoraires/'
        api_call_response = self.session.get(API_URL, params={'date': date},
                                             verify=self.auth.config.getboolean('Global', 'validate_ssl'))

        return json.loads(api_call_response.text)

    def getDailyConsumption(self, start_date,end_date):
        """Return hourly consumption for a specific day

        :param: start_date: YYYY-MM-DD string to pass to API
        :param: end_date: YYYY-MM-DD string to pass to API

        :return: raw JSON from hydro QC API
        """
        API_URL = 'https://cl-ec-spring.hydroquebec.com/portail/fr/group/clientele/portrait-de-consommation' \
                  '/resourceObtenirDonneesQuotidiennesConsommation'
        params = {
            'dateDebut': start_date,
            'dateFin': end_date
        }
        api_call_response = self.session.get(API_URL, params=params,
                                             verify=self.auth.config.getboolean('Global', 'validate_ssl'))

        return json.loads(api_call_response.text)

    def getWinterCreditEvents(self, reference_datetime=None):
        """Return winter peak events in a more structured way

        :param: reference_date: YYYY-MM-DD HH:MM:SS date/time string used for testing (should not be used in prod)

        :return:    JSON Object with current_winter, past_winters and next event.
                    Current winter have past and future events
                    Events have timestamp as key (easier to sort) and have date, start hour, end hour
                    events :
                        {
                            'current_winter': {
                                'past': {},
                                'future': {}
                            },
                            'past_winters': {},
                            'next': {}
                        }
                    event :
                        'timestamp': {
                            date: 'YYYY-MM-DD',
                            start : 'HH:MM:SS',
                            end: 'HH:MM:SS'
                        }
        """
        if not reference_datetime:
            ref_date = datetime.datetime.now()
        else:
            ref_date = datetime.datetime.strptime(reference_datetime, '%Y-%m-%d %H:%M:%S')
        data = self.getWinterCredit()
        events = {
            'current_winter': {
                'past': {},
                'future': {}
            },
            'past_winters': {},
            'next': {}
        }
        if 'periodesEffacementsHivers' in data:
            for season in data['periodesEffacementsHivers']:
                winter_start = parser.isoparse(season['dateDebutPeriodeHiver']).date()
                winter_end = parser.isoparse(season['dateFinPeriodeHiver']).date()
                if winter_start <= datetime.date.today() <= winter_end:
                    current = True
                else:
                    current = False

                if 'periodesEffacementHiver' in season:
                    for event in season['periodesEffacementHiver']:
                        e = {}
                        date = parser.isoparse(event['dateEffacement'])
                        e['date'] = date.strftime('%Y-%m-%d')
                        e['start'] = event['heureDebut']
                        e['end'] = event['heureFin']
                        start_date_time = datetime.datetime.strptime(e['date'] + " " + e['start'], '%Y-%m-%d %H:%M:%S')
                        timestamp = start_date_time.timestamp()
                        future = False
                        if start_date_time > ref_date:
                            future = True
                        if current:
                            if future:
                                events['current_winter']['future'][timestamp] = e
                            else:
                                events['current_winter']['past'][timestamp] = e
                        else:
                            events['past_winter'][timestamp] = e

            if events['current_winter']['future']:
                next_event = min(events['current_winter']['future'], key=float)
                if next_event:
                    events['next'] = {next_event: events['current_winter']['future'][next_event]}

        return events
