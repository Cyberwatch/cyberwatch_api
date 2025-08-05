#!/usr/bin/env python

from cyberwatch_api import Cyberwatch_Pyhelper
import sys
from cbw_cli.bin import os, airgap
import requests
from urllib3.exceptions import InsecureRequestWarning

# Disable certificate check warnings
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def help():
    print("Usage : cyberwatch-cli [OPTIONS] [COMMAND] [ARGS]")
    print("---")
    print("Cli to interact with Cyberwatch API.\n")
    print("\n")
    print("\t{: <15} \t {}".format("OPTIONS", "DESCRIPTION"))
    print("\t{: <15} \t {}".format("---", "---"))
    print("\t{: <15} \t {}".format("--verify-ssl", "Using this options, SSL verification will be done"))
    print("\t{: <15} \t {}".format("--api-url", "Set the URL of the Cyberwatch API"))
    print("\t{: <15} \t {}".format("--api-key", "Set the KEY of the Cyberwatch API"))
    print("\t{: <15} \t {}".format("--api-secret", "Set the SECRET KEY of the Cyberwatch API"))
    print("\n")
    print("{: >15} \t {}".format("COMMAND", "DESCRIPTION"))
    print("{: >15} \t {}".format("---", "---"))
    print("{: >15} \t {}".format("os", "Manage cyberwatch operating systems"))
    print("{: >15} \t {}".format("airgap", "Interact with the airgap interface"))
    print("{: >15} \t {}".format("ping", "Ping the Cyberwatch API to validate the connexion"))
    print("\n")

def ping(CBW_API, verify_ssl=False, verbose=False):
    apiResponse = CBW_API.request(
        method="GET",
        endpoint="/api/v3/ping",
        verify_ssl=verify_ssl
    )
    if verbose:
        print("Trying to ping Cyberwatch API...")
    response = next(apiResponse).json()
    if verbose:
        print(response)
    if response.get("error") is not None:
        print("Failed ping to Cyberwatch API, exiting...")
        sys.exit(1)

def main():
    arguments = sys.argv[1:]

    try:
        # Check if we should verify the SSL Certificate
        VERIFY_SSL = False
        if "--verify-ssl" in arguments:
            VERIFY_SSL = True
            arguments.remove("--verify-ssl")
        
        # Initializing API Client
        try:
            # Parsing API DATA if specified in command line
            API_DATA = [None, None, None]
            for index, data in enumerate(["--api-url", "--api-key", "--api-secret"]):
                if data in arguments and len(arguments) > arguments.index(data) + 1:
                    API_DATA[index] = arguments[arguments.index(data) + 1]
                    arguments.remove(data)
                    arguments.remove(API_DATA[index])
            # Creating API Client
            CBW_API = Cyberwatch_Pyhelper(api_url = API_DATA[0], api_key = API_DATA[1], api_secret = API_DATA[2])
        except Exception as e: # Catching error raised by API Client if not api data is found (via arguments, api.conf or environnement variables)
            help()
            print("[-] ERROR : " + str(e))
            sys.exit(1)

        if not arguments or arguments[0] == "help":
            help()
        elif arguments[0] == "ping":
            ping(CBW_API, VERIFY_SSL, True)
        elif arguments[0] == "os":
            ping(CBW_API, VERIFY_SSL)
            os.manager(arguments[1:], CBW_API, VERIFY_SSL)
        elif arguments[0] == "airgap":
            ping(CBW_API, VERIFY_SSL)
            airgap.manager(arguments[1:], CBW_API, VERIFY_SSL)
        else:
            print("ERROR : '" + str(arguments[0]) + "' is not a valid command\n---", file=sys.stderr)
            help()
    except Exception as exception:
        print(exception)
        sys.exit(1)

if __name__ == "__main__":
    main()
