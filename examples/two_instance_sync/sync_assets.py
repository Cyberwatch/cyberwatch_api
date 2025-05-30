import os
from cyberwatch_api import Cyberwatch_Pyhelper
from urllib3.exceptions import InsecureRequestWarning
import warnings

warnings.simplefilter('ignore', InsecureRequestWarning)
OUTPUT_DIR = "export" 

def retrieve_assets():
    """Retrieve all assets for a cyberwatch node."""
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

if OUTPUT_DIR:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

ALL_ASSETS = retrieve_assets()

for hostname in ALL_ASSETS:
    output = Cyberwatch_Pyhelper().request(
        method="GET",
        endpoint=f"/api/v3/vulnerabilities/servers/{ALL_ASSETS[hostname]}/info",
        verify_ssl=False
    )
    safe_filename = f"{hostname}.txt".replace('/', '-')
    filepath = os.path.join(OUTPUT_DIR or ".", safe_filename)
    
    with open(filepath, 'wb') as f:
        f.write((next(output).text).encode())
