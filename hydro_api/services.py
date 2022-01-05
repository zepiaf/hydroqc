import logging
import json

import datetime
from .auth import Hydro

log = logging.getLogger(__name__)

class Services:
    def __init__(self):
        self.auth = Hydro()
        self.auth.login()
        self.api_headers = self.auth.get_api_headers()
        self.session = self.auth.session

    def getWinterCredit(self):
        """Return information about the winter credit"""
        API_URL = "https://cl-services.idp.hydroquebec.com/cl/prive/api/v3_0/tarificationDynamique/creditPointeCritique"
        params = {
            'noContrat': self.auth.contract_id
        }
        api_call_response = self.session.get(API_URL, headers=self.api_headers, params=params,
                                             verify=self.auth.config.getboolean('Global', 'validate_ssl'))
        return json.loads(api_call_response.text)

    def getTodayHourlyConsumption(self):
        """Return latest consumption info (about 2h delay it seems)"""
        date = datetime.date
        today = date.today().strftime('%Y-%m-%d')
        yesterday = (date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        # We need to call a valid date first as theoretically today is invalid
        # and the api will not respond if called directly
        self.getHourlyConsumption(yesterday)
        return self.getHourlyConsumption(today)

    def getHourlyConsumption(self, date):
        """Return hourly consumption for a specific day"""
        API_URL = 'https://cl-ec-spring.hydroquebec.com/portail/fr/group/clientele/portrait-de-consommation' \
                  '/resourceObtenirDonneesConsommationHoraires/'
        api_call_response = self.session.get(API_URL, params={'date': date},
                                             verify=self.auth.config.getboolean('Global', 'validate_ssl'))

        return json.loads(api_call_response.text)

    def getDailyConsumption(self, start_date,end_date):
        """Return hourly consumption for a specific day"""
        API_URL = 'https://cl-ec-spring.hydroquebec.com/portail/fr/group/clientele/portrait-de-consommation' \
                  '/resourceObtenirDonneesQuotidiennesConsommation'
        params = {
            'dateDebut': start_date,
            'dateFin': end_date
        }
        api_call_response = self.session.get(API_URL, params=params,
                                             verify=self.auth.config.getboolean('Global', 'validate_ssl'))

        return json.loads(api_call_response.text)

