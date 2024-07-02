import os
import logging
import traceback

from swan.api.swan_api import Orchestrator
from swan.api_client import APIClient
from swan.common.constant import *
from swan.common.exception import SwanAPIException

class Session:
    """
    A session stores configuration states
    """

    def __init__(
        self,
        api_key: str = None,
        login_url: str = None,
        login: bool = True, 
    ):
        
        self.token = None
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.getenv("API_KEY")
        
        if login_url:
            self.login_url = login_url
        else:
            self.login_url = SWAN_API
        self.api_client = APIClient()
        self.login = login
        if login:
            self.api_key_login()

    
    def api_key_login(self):
        """Login with Orchestrator API Key.

        Returns:
            A str access token for further Orchestrator API access in
            current session.
        """
        params = {"api_key": self.api_key}
        try:
            result = self.api_client._request_with_params(
                POST, SWAN_APIKEY_LOGIN, self.login_url, params, None, None
            )
            if result["status"] == "failed":
                raise SwanAPIException("Login Failed")
            self.token = result["data"] 
            logging.info("Login Successfully!")
        except SwanAPIException as e:
            logging.error(e.message)
        except Exception as e:
            logging.error(str(e) + traceback.format_exc())
    
    # login = False, because should already be logged into session
    def resource(self, service_name: str, login=False, url_endpoint=None, verification=True):
        if url_endpoint == None:
            url_endpoint = self.login_url
        if service_name.lower() == 'orchestrator':
            resource = Orchestrator(api_key=self.api_key, url_endpoint=url_endpoint, token=self.token, login=login, verification=verification)
        
        return resource
        