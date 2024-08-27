from cyberwatch_api import Cyberwatch_Pyhelper
import json
import requests
import configparser
import urllib3
urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

def jprint(text):
    print(json.dumps(text, indent=4))
    return json.dumps(text, indent=4)

def cbw_createAirgapAsset(HOSTNAME, TECHNOLOGIES):
    output = "HOSTNAME:{}\n".format(HOSTNAME)
    # for TECHNOLOGIE in TECHNOLOGIES:
    #     (package, version) = TECHNOLOGIE.split("_")
    #     output += "NVD_APPLICATION:(from nessus : unanalyzed) {}|{}\n".format(package, version)

    apiResponse = Cyberwatch_Pyhelper().request(
        method="POST",
        endpoint="/api/v2/cbw_scans/scripts",
        body_params={
            "output" : output
        },
        timeout=90,
        verify_ssl=False
    )
    result = next(apiResponse)

    if 'error' in result:
        raise "ERROR : " + result["error"]["message"]
    return result.json()["server_id"]


def cbw_deleteAsset(id):
    apiResponse = Cyberwatch_Pyhelper().request(
        method="DELETE",
        endpoint="/api/v3/assets/servers/{}".format(id),
        verify_ssl=False,
    )

    return next(apiResponse).json()   

def cbw_retrieveSecurityIssue(sid):
    apiResponse = Cyberwatch_Pyhelper().request(
        method="GET",
        endpoint="/api/v3/security_issues",
        verify_ssl=False,
        body_params={
            "sid" : sid,
        }
    )

    return next(apiResponse).json()

def cbw_deleteSecurityIssue(id):
    apiResponse = Cyberwatch_Pyhelper().request(
        method="DELETE",
        endpoint="/api/v3/security_issues/{}".format(id),
        verify_ssl=False,
    )

    return next(apiResponse).json()

def cbw_createSecurityIssue(sid, title, cve_announcements, servers):
    apiResponse = Cyberwatch_Pyhelper().request(
        method="POST",
        endpoint="/api/v3/security_issues",
        verify_ssl=False,
        body_params={
            "sid" : sid,
            "title" : title,
            "cve_announcements" : cve_announcements,
            "servers" : servers,
        }
    )

    return next(apiResponse).json()

def cbw_refreshAssetAnalysis(server_id):
    apiResponse = Cyberwatch_Pyhelper().request(
        method="PUT",
        endpoint="/api/v3/vulnerabilities/servers/{}/refresh".format(server_id),
        verify_ssl=False,
    )

    return next(apiResponse).json()

def cbw_clearNessusData():
    #####
    # Clear All Nessus Security Issues
    #####

    apiResponse = Cyberwatch_Pyhelper().request(
        method="GET",
        endpoint="/api/v3/security_issues",
        verify_ssl=False,
    )

    security_issues = []
    for page in apiResponse:
        security_issues = security_issues + page.json()

    for security_issue in security_issues:
        if security_issue["title"].startswith(PARSE_CONFIG()["SCRIPT_ASSET_IDENTIFIER"]):
            print("Deleting Security Issue {}".format(security_issue["title"]))
            cbw_deleteSecurityIssue(security_issue["id"])
    
    #####
    # Clear All Nessus Assets
    #####
    
    apiResponse = Cyberwatch_Pyhelper().request(
        method="GET",
        endpoint="/api/v3/assets/servers",
        verify_ssl=False,
    )
    print("Retrieving assets : 0")
    assets = []
    for page in apiResponse: 
        assets = assets + page.json()
        print("\033[A\033[A\nRetrieving assets : " + str(len(assets)))
    
    for asset in assets:
        if asset["hostname"].startswith(PARSE_CONFIG()["SCRIPT_ASSET_IDENTIFIER"]):
            print("Deleting Asset {}".format(asset["hostname"]))
            cbw_deleteAsset(asset["id"])

def PARSE_CONFIG():
    config = configparser.ConfigParser()
    config.read('api.conf')
    NESSUS_API_KEY = config['nessus']['api_key']
    NESSUS_SECRET_KEY = config['nessus']['secret_key']
    NESSUS_URL = config['nessus']['url']
    SCRIPT_DEBUG = config['script']['debug']
    SCRIPT_ASSET_IDENTIFIER = config['script']['asset_identifier']

    return {
        "NESSUS_API_KEY" : NESSUS_API_KEY,
        "NESSUS_SECRET_KEY" : NESSUS_SECRET_KEY,
        "NESSUS_URL" : NESSUS_URL,
        "SCRIPT_DEBUG" : "true" in SCRIPT_DEBUG.lower(),
        "SCRIPT_ASSET_IDENTIFIER" : SCRIPT_ASSET_IDENTIFIER
    }

def NESSUS_API(URL):
    nessus_config = PARSE_CONFIG()
    return requests.get(URL, headers={'X-ApiKeys': f'accessKey={nessus_config["NESSUS_API_KEY"]}; secretKey={nessus_config["NESSUS_SECRET_KEY"]}'}, verify=False)
