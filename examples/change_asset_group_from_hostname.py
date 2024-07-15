# This script will replace asset's groups by another one
from cyberwatch_api import Cyberwatch_Pyhelper
import requests
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

####################################################
########## Définition des variables ################
####################################################
 
idgrp = 10 # Id du groupe qui écrasera ceux existant sur les actifs 
 
####################################################
 
def retrieve_assets():
    """retrieve all assets for a cyberwatch node"""
    assets = {}
    apiResponse = Cyberwatch_Pyhelper().request(
        method="GET",
        endpoint="/api/v3/vulnerabilities/servers",
        verify_ssl=False
    )
    print("Retrieving assets : 0")
    for page in apiResponse:
        for asset in page.json():
            assets[asset['hostname']] = asset['id']
        print("\033[A\033[A\nRetrieving assets : " + str(len(assets)))
    return assets
 
ALL_ASSETS = retrieve_assets()
 
with open('liste_machines', 'r') as f:
    hostnames = [line.strip() for line in f]
 
for hostname in hostnames:
    output = Cyberwatch_Pyhelper().request(
        method="PUT",
        endpoint="/api/v3/vulnerabilities/servers/" + str(ALL_ASSETS.get(hostname)),
        body_params={'groups' : [idgrp]},
        verify_ssl=False
    )
    next(output)