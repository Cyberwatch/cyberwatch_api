from cyberwatch_api import Cyberwatch_Pyhelper
from datetime import datetime

def format_date(d):
    date_object = datetime.strptime(d, '%Y-%m-%dT%H:%M:%S.%f%z')
    return date_object.strftime('%d/%m/%Y')

def retrieve_assets():
    """retrieve all assets for a cyberwatch node"""
    assets = []
    apiResponse = Cyberwatch_Pyhelper().request(
        method="GET",
        endpoint="/api/v3/vulnerabilities/servers",
    )
    print("Retrieving assets : 0")
    for page in apiResponse: 
        assets = assets + page.json()
        print("\033[A\033[A\nRetrieving assets : " + str(len(assets)))
    return assets

def retrieve_asset_cves_patches(assetID):
    """retrieve all available patches for a given asset"""
    apiResponse = Cyberwatch_Pyhelper().request(
        method="GET",
        endpoint="/api/v3/vulnerabilities/servers/" + str(assetID),
    )
    asset = next(apiResponse).json()
    return (asset["cve_announcements"], asset["updates"])

def launch_script():
    assets = retrieve_assets()
    print("[+] " + str(len(assets)) + " assets were found on this cyberwatch node")
    if not assets:
        return

    assets_with_KB_patch_available = {} # All assets with at least one KB patch available

    for asset in assets:
        cveList, patchList = retrieve_asset_cves_patches(asset["id"])
        KBPatches = [patch for patch in patchList if patch["target"] and patch["target"]["product"].startswith('KB')] # Retrieving all KB patches

        if KBPatches: # If at least one KB patch is available
            oldest_KB_CVEs_detection_date = [] 
            for KB in KBPatches: 
                single_kb_cves_detection_date = [CVE["detected_at"] for CVE in cveList if CVE["cve_code"] in KB["cve_announcements"]]
                if single_kb_cves_detection_date:
                    oldest_KB_CVEs_detection_date.append(min(single_kb_cves_detection_date))  # Retrieving the oldest CVE Announcement detection date for each KB patch
            
            oldest_CVE_label = ""
            if oldest_KB_CVEs_detection_date: # If at least a date is available, we find the most recent one
                oldest_CVE_label = " | No Windows Update since at least : " + format_date(max(oldest_KB_CVEs_detection_date)) # Getting the most recent CVE annoncement out of all the oldest for each KB patch

            print("[+] Asset ID : " + str(asset["id"]) +  oldest_CVE_label)
            print("\t- " + ", ".join([patch["target"]["product"] for patch in KBPatches]))
            assets_with_KB_patch_available[asset["id"]] = str(len(KBPatches))

launch_script()
