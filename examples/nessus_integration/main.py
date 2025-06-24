from cbw_helper import (
    PARSE_CONFIG,
    NESSUS_API,
    cbw_clearNessusData,
    cbw_createAirgapAsset,
    cbw_retrieveSecurityIssue,
    cbw_deleteSecurityIssue,
    cbw_createSecurityIssue
)
import urllib3
urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

#####
# Initializing global variables
#####
NESSUS_URL = PARSE_CONFIG()["NESSUS_URL"]
DEBUG = PARSE_CONFIG()["SCRIPT_DEBUG"]
NESSUS_ASSETS = {}

#####
# Retrieving all Nessus Scans
#####

SCANS = NESSUS_API('{}/scans'.format(NESSUS_URL)).json()["scans"]

for SCAN in SCANS:
    print("[+] Nessus - Retrieving scan {}".format(SCAN["id"]))
    #####
    # Retrieve all hosts associated to the current scan
    #####
    HOSTS = NESSUS_API('{}/scans/{}'.format(NESSUS_URL, SCAN["id"])).json()["hosts"]

    for HOST in HOSTS:
        print("\t Host : {}".format(HOST["hostname"]))
        #####
        # Clean the previous host data
        #####
        CVE_LIST = []

        #####
        # Get the current host informations and plugins list
        #####
        HOST_ID = HOST["host_id"]
        HOST_NAME = HOST["hostname"]
        HOST_INFORMATIONS = NESSUS_API('{}/scans/{}/hosts/{}'.format(NESSUS_URL, SCAN["id"], HOST_ID)).json()
        HOST_PLUGINS_LIST = list(set([CVE["plugin_id"] for CVE in HOST_INFORMATIONS["vulnerabilities"] if CVE["plugin_id"]]))
        print("\t\t Plugins : {}".format(len(HOST_PLUGINS_LIST)))

        #####
        # For each plugin, retrieve the associated CVEs
        #####
        for PLUGIN in HOST_PLUGINS_LIST:
            try:
                URL = '{}/scans/{}/hosts/{}/plugins/{}'.format(NESSUS_URL, SCAN["id"], HOST_ID, PLUGIN)
                RESPONSE = NESSUS_API(URL)
                CVE_LIST = list(set(CVE_LIST + next(ref["values"]["value"] for ref in NESSUS_API(URL).json()["info"]["plugindescription"]["pluginattributes"]["ref_information"]["ref"] if ref["name"] == "cve")))
            except Exception:
                pass

        #####
        # If it is the first time we find the host, we save it. Otherwise, we just append the found CVEs
        #####

        if HOST_NAME not in NESSUS_ASSETS:
            NESSUS_ASSETS[HOST_NAME] =      {
                "id" : HOST_ID,
                "hostname" : HOST_NAME,
                "cve_list" : CVE_LIST,
            }
        else:
            NESSUS_ASSETS[HOST_NAME]["cve_list"] = list(set(NESSUS_ASSETS[HOST_NAME]["cve_list"] + CVE_LIST))
        
        print("\t\t Total CVEs : {}".format(len(NESSUS_ASSETS[HOST_NAME]["cve_list"])))

#####
# Clean cyberwatch data related to nessus
#####
print("[+] Cleaning all related Nessus data on Cyberwatch")
cbw_clearNessusData()

#####
# Foreach found nessus host, we create a security issue linking all the found CVEs, then we associate it to the matching airgap asset
#####

for NESSUS_ASSET_ID, NESSUS_ASSET in NESSUS_ASSETS.items():
    #####
    # Creating or updating the airgap asset
    #####
    CBW_ASSET_HOSTNAME = "Nessus | {}".format(NESSUS_ASSET["hostname"])
    CBW_ASSET_ID = cbw_createAirgapAsset(CBW_ASSET_HOSTNAME, [])
    print("[+] Cyberwatch - Creating asset {}".format(CBW_ASSET_HOSTNAME))

    #####
    # Creating the security issue
    #####
    CBW_HOST_SID = "Nessus_{}".format(NESSUS_ASSET["hostname"])
    CBW_HOST_SID_TITLE = "Nessus | {}".format(NESSUS_ASSET["hostname"])

    if bool(cbw_retrieveSecurityIssue(CBW_HOST_SID)): # Security Issues Already Exists
        cbw_deleteSecurityIssue(cbw_retrieveSecurityIssue(CBW_HOST_SID)[0]["id"])
    
    cbw_createSecurityIssue(CBW_HOST_SID, CBW_HOST_SID_TITLE, NESSUS_ASSET["cve_list"], [CBW_ASSET_ID])