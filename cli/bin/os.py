from cyberwatch_api import Cyberwatch_Pyhelper
from . import verify_ssl_value
import sys

def help():
    print("Usage : " + str(sys.argv[0]) + " os [COMMAND] [ARGS]")
    print("---")
    print("Manage cyberwatch operating systems.\n")
    print("{: >10} \t {}".format("COMMAND", "DESCRIPTION"))
    print("{: >10} \t {}".format("---", "---"))
    print("{: >10} \t {}".format("list", "List all operating systems"))
    print("\n")

def retrieve_os():
    apiResponse = Cyberwatch_Pyhelper().request(
        method="GET",
        endpoint="/api/v3/os",
        verify_ssl=verify_ssl_value()
    )
    os = []
    for page in apiResponse: 
        os = os + page.json()
    return os

def manager(arguments):
    if not arguments or arguments[0] == "help":
        help()

    elif arguments[0] == "list":
        print("{:<32} {:<27} {:<13}".format("KEY", "SHORT NAME", "ARCH"))
        print("{:<32} {:<27} {:<13}".format("---", "---", "---"))
        for single_os in retrieve_os():
            print("{:<32} {:<27} {:<13}".format(single_os["key"], single_os["short_name"], single_os["arch"] if single_os["arch"] else "-"))

    else:
        print("ERROR : '" + str(arguments[0]) + "' is not a valid subcommand\n---", file=sys.stderr)
        help()
