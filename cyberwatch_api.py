"""Cyberwatch API Python Helper"""
import os
import json
from configparser import ConfigParser
from typing import Generator
import requests

class Cyberwatch_Pyhelper:
    CONF = ConfigParser()

    def __init__(self, **kwargs):
        self.path_to_conf = kwargs.get("path_to_conf")
        self.api_url = kwargs.get("api_url")
        self.api_key = kwargs.get("api_key")
        self.api_secret = kwargs.get("api_secret")

    @property
    def path_to_conf(self) -> str:
        return self.__path_to_conf

    @path_to_conf.setter
    def path_to_conf(self, value: str):
        # We search for a file named api.conf in the given path
        # Take user input
        if value is not None:
            self.__path_to_conf = os.path.join(value, "api.conf")
        # Else search for config file in current working directory
        else:
            directory = os.getcwd()
            self.__path_to_conf = os.path.join(directory, "api.conf")
        # If still not found, search in parent directory of cwd
        if len(self.CONF.read(self.__path_to_conf)) == 0:
            self.__path_to_conf = os.path.join(os.path.dirname(directory), "api.conf")
        # If no conf file was found set it to None
        if len(self.CONF.read(self.__path_to_conf)) == 0:
            self.__path_to_conf = None

    @property
    def api_url(self) -> str:
        return self.__api_url

    def clear_endpoint(f):
        """
        Decorator that takes the endpoint that was given by the API user,
        and replaces the {parameter} by the one that was given inside the params or body params dict
        """
        def wrapper(*args, **kwargs):
            endpoint = kwargs.get("endpoint")
            parameters = [parameter.split("}")[0] for parameter in endpoint.split("{")[1:]]

            for parameter in parameters:
                parameter_value = (kwargs.get("params",{}).get(parameter) or kwargs.get("body_params",{}).get(parameter))
                endpoint = endpoint.replace("{" + parameter + "}", str(parameter_value))
                # Deleting the 'parameter' from the kwargs arguments if it exists
                [kwargs[key].pop(parameter, "") for key in kwargs if type(kwargs[key]) == dict]

            kwargs.update({"endpoint": endpoint})
            return f(*args, **kwargs)
        return wrapper

    @api_url.setter
    def api_url(self, value: str):
        """
        This setter will search for a parameter given during the initialization of the class.
        If not found it will search inside the CONF file if given.
        If not found it will search inside the env.
        """
        if value:
            self.__api_url = value
        elif self.path_to_conf is not None:
            self.__api_url = self.CONF.get("cyberwatch", "url")
        else:
            self.__api_url = os.getenv("api_url")
        if self.__api_url is None:
            raise Exception("api_url not found")

    @property
    def api_key(self) -> str:
        return self.__api_key

    @api_key.setter
    def api_key(self, value: str):
        """
        This setter will search for a parameter given during the initialization of the class.
        If not found it will search inside the CONF file if given.
        If not found it will search inside the env.
        """
        if value:
            self.__api_key = value
        elif self.path_to_conf is not None:
            self.__api_key = self.CONF.get("cyberwatch", "api_key")
        else:
            self.__api_key = os.getenv("api_key")
        if self.__api_key is None:
            raise Exception("api_key not found")

    @property
    def api_secret(self) -> str:
        return self.__api_secret

    @api_secret.setter
    def api_secret(self, value: str):
        """
        This setter will search for a parameter given during the initialization of the class.
        If not found it will search inside the CONF file if given.
        If not found it will search inside the env.
        """
        if value:
            self.__api_secret = value
        elif self.path_to_conf is not None:
            self.__api_secret = self.CONF.get("cyberwatch", "secret_key")
        else:
            self.__api_secret = os.getenv("api_secret")
        if self.__api_secret is None:
            raise Exception("api_secret not found")

    @property
    def method(self) -> str:
        return self.__method

    @method.setter
    def method(self, value: str):
        if isinstance(value, str):
            self.__method = str(value).upper()
        else:
            raise Exception("The type of method parameter should be a str")

    @property
    def url(self) -> str:
        return self.__url

    @url.setter
    def url(self, value: str):
        if isinstance(value, str):
            self.__url = self.api_url + value
        else:
            raise Exception("The type of endpoint parameter should be str")

    @property
    def timeout(self) -> int:
        return self.__timeout

    @timeout.setter
    def timeout(self, value: int):
        if isinstance(value, int):
            self.__timeout = value
        else:
            raise Exception("The type of timeout parameter should be int")

    def __basic_auth(self) -> requests.auth.HTTPBasicAuth:
        """
        Private method returning a BasicAuth
        """
        return requests.auth.HTTPBasicAuth(self.api_key, self.api_secret)
    
    def api_http_request(self, url):
        return requests.request(
            method=self.method,
            url=url,
            headers=self.headers,
            auth=self.__basic_auth(),
            params=self.params,
            data=self.body_params,
            timeout=self.timeout,
            verify=self.verify_ssl
        )
    
    @clear_endpoint
    def request(self, **kwargs) -> Generator[requests.models.Response, None, None]:
        """
        Only accessible method, handles every step of the API call
        """
        self.method = kwargs.get("method")
        self.url = kwargs.get("endpoint")
        self.timeout = kwargs.get("timeout") or 10
        self.params = kwargs.get("params") or {}
        self.body_params = kwargs.get("body_params") or {}

        self.headers = {'Content-type': 'application/json'}

        if self.body_params is not None:
            self.body_params = json.dumps(self.body_params)

        self.verify_ssl = kwargs.get("verify_ssl")

        response = self.api_http_request(self.url)
        yield response
        while "next" in response.links:
            response = self.api_http_request(response.links["next"]["url"])
            yield response


if __name__ == "__main__":
    Cyberwatch_Pyhelper()
