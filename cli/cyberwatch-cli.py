#!/usr/bin/env python

from cyberwatch_api import Cyberwatch_Pyhelper
import sys
from bin import os, airgap
import requests
from urllib3.exceptions import InsecureRequestWarning

# Disable certificate check warnings
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def help():
    print("Usage : " + str(sys.argv[0]) + " [--verify_ssl] [COMMAND] [ARGS]")
    print("---")
    print("Cli to interact with Cyberwatch API.\n")
    print("{: >15} \t {}".format("--verify-ssl", "Using this options, SSL verification will be done"))
    print("\n")
    print("{: >15} \t {}".format("COMMAND", "DESCRIPTION"))
    print("{: >15} \t {}".format("---", "---"))
    print("{: >15} \t {}".format("os", "Manage cyberwatch operating systems"))
    print("{: >15} \t {}".format("airgap", "Interact with the airgap interface"))
    print("\n")

arguments = sys.argv[1:]

try:
    # Check if we should verify the SSL Certificate
    VERIFY_SSL = False
    if "--verify-ssl" in arguments:
        VERIFY_SSL = True
        arguments.remove("--verify-ssl")

    if not arguments or arguments[0] == "help":
        help()
    elif arguments[0] == "os":
        os.manager(arguments[1:], VERIFY_SSL)
    elif arguments[0] == "airgap":
        airgap.manager(arguments[1:], VERIFY_SSL)
    else:
        print("ERROR : '" + str(arguments[0]) + "' is not a valid command\n---", file=sys.stderr)
        help()
except Exception as exception:
    print(exception)
    sys.exit(1)
