"""
Script that expects a hostname as an input and prints the CVSSv3 strings of all the assets'
CVEs as a result
"""

import sys

from cyberwatch_api import Cyberwatch_Pyhelper

import cve_code_to_cvss

def main(hostname):
    """Return CVSS vector of an asset from its hostname"""

    try:
        asset_id = next(Cyberwatch_Pyhelper().request(
            method="get",
            endpoint=f"/api/v3/vulnerabilities/servers/?hostname={hostname}",
            params = {"per_page": 100},
            verify_ssl=True
        )).json()[0]["id"]
    except IndexError:
        print(f"hostname {hostname} not found on your Cyberwatch instance")
        return 1

    asset_details = Cyberwatch_Pyhelper().request(
        method="get",
        endpoint=f"/api/v3/vulnerabilities/servers/{asset_id}",
        params = {"per_page": 100},
        verify_ssl=False
    )

    for cve in next(asset_details).json()["cve_announcements"]:
        # Call module
        if cve["active"] is True:
            cvss_string = cve_code_to_cvss.retrieve_cvss_string(cve["cve_code"])
            print(f"{cve['cve_code']} : {cvss_string}")

    return 0

if __name__ == "__main__":
    main(sys.argv[1])
