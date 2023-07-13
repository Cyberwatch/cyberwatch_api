#!/usr/bin/env python

from cyberwatch_api import Cyberwatch_Pyhelper
import sys
from bin import os, airgap

def help():
    print("Usage : " + str(sys.argv[0]) + " [COMMAND] [ARGS]")
    print("---")
    print("Cli to interact with Cyberwatch API.\n")
    print("{: >10} \t {}".format("COMMAND", "DESCRIPTION"))
    print("{: >10} \t {}".format("---", "---"))
    print("{: >10} \t {}".format("os", "Manage cyberwatch operating systems"))
    print("{: >10} \t {}".format("airgap", "Interact with the airgap interface"))
    print("\n")

arguments = sys.argv[1:]

try:
    if not arguments or arguments[0] == "help":
        help()
    elif arguments[0] == "os":
        os.manager(arguments[1:])
    elif arguments[0] == "airgap":
        airgap.manager(arguments[1:])
    else:
        print("ERROR : '" + str(arguments[0]) + "' is not a valid command\n---", file=sys.stderr)
        help()
except Exception as exception:
    print(exception)
    sys.exit(1)
