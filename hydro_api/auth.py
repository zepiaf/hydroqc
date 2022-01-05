"""
Authentication and initialization of Hydro API
"""
import configparser
import json
import random
import string
import uuid
import requests
import logging

log = logging.getLogger(__name__)

from datetime import datetime

class Hydro:
    """
    Hydro API

    Defines Hydro API URL and methods to login and initialize the API
    Hydro API is composed of several components that are using different method for authentication
    The initial login phase is achieved via oauth2 and the rest use session cookies to carry the authentication.
    """

    # OAUTH uri
    SECURITY_URL='https://session.hydroquebec.com/config/security.json'
    AUTH_URL = "https://connexion.hydroquebec.com:443/hqam/json/realms/root/realms/clients/authenticate"
    AUTHORIZE_URL = "https://connexion.hydroquebec.com:443/hqam/oauth2/authorize"
    TOKEN_URL = "https://connexion.hydroquebec.com:443/hqam/oauth2/access_token"

    # Initialization uri
    RELATION_URL = "https://cl-services.idp.hydroquebec.com/cl/prive/api/v1_0/relations"
    INFOBASE_URL = "https://cl-services.idp.hydroquebec.com/cl/prive/api/v3_0/partenaires/infoBase"
    SESSION_URL = "https://cl-ec-spring.hydroquebec.com/portail/prive/maj-session/"
    CONTRACT_URL = "https://cl-services.idp.hydroquebec.com/cl/prive/api/v3_0/partenaires/" \
                   "calculerSommaireContractuel?indMAJNombres=true"
    PORTRAIT_URL = "https://cl-ec-spring.hydroquebec.com/portail/fr/group/clientele/portrait-de-consommation/"

    def __init__(self, **kwargs):
        """Initialize parameters from the config file and hydro OAUTH2 settings URL"""
        self.session = requests.Session()
        self.config = configparser.ConfigParser()
        self.config.read('config/config.ini')
        if not self.config.getboolean('Global', 'validate_ssl'):
            from urllib3.exceptions import InsecureRequestWarning
            requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        self.login_data = {}
        self.token_id = ""
        self.oauth2_settings = self.set_oauth_settings()
        self.guid = str(uuid.uuid1())
        self.callback_uri = self.oauth2_settings['redirectUri']
        self.state = "".join(random.choice(string.digits + string.ascii_letters) for i in range(40))
        self.nonce = self.state
        self.access_token = ""
        self.account_id = ""
        self.customer_id = ""
        self.contract_id = ""

    def set_oauth_settings(self):
        """Read OAUTH2 settings from hydro json"""
        data = self.session.get(self.SECURITY_URL, verify=self.config.getboolean('Global', 'validate_ssl'))
        try:
            return data.json()['oauth2'][0]
        except:
            return {}

    def login(self):
        """Full login

        Perform all necessary actions to login and get the "session" opened to use hydro API.

        1. authenticate
        2. get an access token
        3. get user information and hit the pages needed to initialize the session
        """
        try:
            log.debug('authenticating')
            self._auth()
        except:
            log.error('authentication failed')
            return False
        if not self.access_token:
            try:
                log.debug('getting token')
                self.access_token = self._get_token()
            except:
                log.error('token acquisition failed')
                return False
        if not self.customer_id or not self.account_id or not self.contract_id:
            try:
                log.debug('getting account info')
                self._get_account_info()
            except:
                log.debug('failed to get account info')
                return False
        return True

    def _auth(self):
        """OAUTH2 authentication"""
        log.debug("performing authentication")
        headers = {
            "Content-Type": "application/json",
            "X-NoSession": "true",
            "X-Password": "anonymous",
            "X-Requested-With": "XMLHttpRequest",
            "X-Username": "anonymous"
        }

        try:
            resource = self.session.post(self.AUTH_URL, headers=headers,
                                         verify=self.config.getboolean('Global', 'validate_ssl'))
        except Exception as e:
            log.error('shit happend')
        try:
            data = resource.json()
            self.login_data = data
        except:
            log.error('unable to get data')
        if 'tokenId' not in self.login_data and 'callbacks' in self.login_data:
            log.debug("no token id but data has callback")
            # Fill the callback template
            self.login_data['callbacks'][0]['input'][0]['value'] = self.config.get('Credentials','user')
            self.login_data['callbacks'][1]['input'][0]['value'] = self.config.get('Credentials','password')

            json_data = json.dumps(self.login_data)
            try:
                log.debug("trying to get a token")
                res = self.session.post(self.AUTH_URL, data=json_data, headers=headers,
                                        verify=self.config.getboolean('Global', 'validate_ssl'))
            except:
                log.error('Unable to connect.')
                return False

            json_res = res.json()
            if 'tokenId' not in json_res:

                log.error('invalid credentials')
                return False

            self.token_id = json_res['tokenId']
            log.debug('Got token %s' % self.token_id)
            return True

        elif self.token_id is not None and 'tokenId' in self.login_data and 'callbacks' in self.login_data:
            log.debug("token id present and not ours and data has callback")
            if self.token_id != self.login_data['tokenId']:
                self.token_id = self.login_data['tokenId']
                log.debug('Authentication successful')
                return True

        else:
            log.error('Something failed in the auth process')
            return False

    def _get_token(self):
        """OAUTH2 access token retrieval. Needed for the IDP api"""
        params = {
            "response_type": "id_token token",
            "client_id": self.oauth2_settings['clientId'],
            "state": self.state,
            "redirect_uri": self.oauth2_settings['redirectUri'],
            "scope": self.oauth2_settings['scope'],
            "nonce": self.nonce,
            "locale": "en"
        }
        resource = self.session.get(self.AUTHORIZE_URL, params=params, allow_redirects=False,
                                    verify=self.config.getboolean('Global', 'validate_ssl'))
        callback_url = resource.headers['Location']
        self.session.get(callback_url, verify=self.config.getboolean('Global', 'validate_ssl'))
        raw_callback_params = callback_url.split('/callback#', 1)[-1].split("&")
        callback_params = dict([p.split("=", 1) for p in raw_callback_params])
        if 'access_token' in callback_params:
            return callback_params['access_token']
        else:
            return ""

    def get_api_headers(self):
        """Headers used by IDP api"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.access_token,
            "NO_PARTENAIRE_DEMANDEUR": self.account_id,
            "NO_PARTENAIRE_TITULAIRE": self.customer_id,
            "DATE_DERNIERE_VISITE": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000+0000"),
            "GUID_SESSION": self.guid
        }
        return headers

    def _get_account_info(self):
        """Retrieve account id, customer id and contract id"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.access_token
        }

        resource = self.session.get(self.RELATION_URL, headers=headers,
                                    verify=self.config.getboolean('Global', 'validate_ssl'))
        data = resource.json()
        try:
            self.account_id = data[0]['noPartenaireDemandeur']
            self.customer_id = data[0]['noPartenaireTitulaire']
        except:
            return False
        params = {"mode": "web"}
        headers = self.get_api_headers()

        self.session.get(self.INFOBASE_URL, headers=headers,
                         verify=self.config.getboolean('Global', 'validate_ssl'))
        self.session.get(self.SESSION_URL, params=params, headers=headers,
                         verify=self.config.getboolean('Global', 'validate_ssl'))

        resource = self.session.get(self.CONTRACT_URL, headers=headers,
                                    verify=self.config.getboolean('Global', 'validate_ssl'))
        data = resource.json()
        if 'comptesContrats' in data:
            try:
                self.contract_id =  data['comptesContrats'][0]['listeNoContrat'][0]
            except:
                log.error('contract not found')
                return False

        self.session.get(self.PORTRAIT_URL, headers=headers, verify=self.config.getboolean('Global', 'validate_ssl'))

        return True

