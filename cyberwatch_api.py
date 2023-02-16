import os
import requests
from configparser import ConfigParser
from typing import Generator


class Cyberwatch_Pyhelper:
    CONF = ConfigParser()

    def __init__(self, *arg, **kwargs):
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
            self.__path_to_conf = os.path.join(
                os.path.dirname(directory), "api.conf")
        # If no conf file was found set it to None
        if len(self.CONF.read(self.__path_to_conf)) == 0:
            self.__path_to_conf = None

    @property
    def api_url(self) -> str:
        return self.__api_url

    def clear_endpoint(f):
        """
        Decorator that takes the endpoint that was given by the API user,
        and replaces the {id} by the id parameter that was given inside the params dict
        """
        def wrapper(*args, **kwargs):
            endpoint = kwargs.get("endpoint")
            if "{id}" in endpoint:
                id = kwargs.get("params").get("id")
                del kwargs["params"]["id"]
                endpoint = endpoint.replace("{id}", str(id))
                kwargs.update({"endpoint": endpoint})
                kwargs["params"].update({"retrieve_all": False})
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
            raise Exception("api_url was not found")

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
        if type(value) is str:
            self.__method = str(value).upper()
        else:
            raise Exception("The type of method parameter should be a str")

    @property
    def url(self) -> str:
        return self.__url

    @url.setter
    def url(self, value: str):
        if type(value) is str:
            self.__url = self.api_url + value
        else:
            raise Exception("The type of endpoint parameter should be str")

    def __basic_auth(self) -> requests.auth.HTTPBasicAuth:
        """
        Private method returning a BasicAuth
        """
        return requests.auth.HTTPBasicAuth(self.api_key, self.api_secret)

    def __basic_params(self, params: dict) -> dict:
        """
        Private Method that sets 'per_page' and 'page' params if they were not given.
        Also sets the 'retrieve_all' parameter to True if it was not set before.
        """
        params.update({"per_page": params.get("per_page", 100)})
        params.update({"page": params.get("page", 1)})
        if self.method == "GET":
            if "ping" not in self.url:
                params.update(
                    {"retrieve_all": params.get("retrieve_all", True)})
        return params

    @clear_endpoint
    def request(
        self, *args, **kwargs
    ) -> Generator[requests.models.Response, None, None]:
        """
        Only accessible method, handles every step of the API call
        """
        self.method = kwargs.get("method")
        self.url = kwargs.get("endpoint")
        params = self.__basic_params(kwargs.get("params"))
        retrieve_all = params.get("retrieve_all")
        response = requests.request(
            method=self.method, url=self.url, auth=self.__basic_auth(), params=params
        )
        # This is necessary because the yield will go infinite for any other method than a 'GET' all, as the API always returns an object.
        # And the while is necessary because we are not told how many pages or how many items there are in the response
        if retrieve_all:
            page = params.get("page")
            yield response
            while response.json() != []:
                page += 1
                params.update({"page": page})
                response = requests.request(
                    method=self.method,
                    url=self.url,
                    auth=self.__basic_auth(),
                    params=params,
                )
                yield response
        else:
            yield response


if __name__ == "__main__":
    Cyberwatch_Pyhelper()
