from cyberwatch_api import Cyberwatch_Pyhelper

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

def retrieve_asset_patches(assetID):
    """retrieve all available patches for a given asset"""
    apiResponse = Cyberwatch_Pyhelper().request(
        method="GET",
        endpoint="/api/v3/vulnerabilities/servers/" + str(assetID),
    )
    return next(apiResponse).json()["updates"]

def launch_script():
    assets = retrieve_assets()
    print("[+] " + str(len(assets)) + " assets were found on this cyberwatch node")
    if not assets: return

    assets_with_KB_patch_available = {} # All assets with at least one KB patch available

    for asset in assets:
        patchList = retrieve_asset_patches(asset["id"])
        patches = [patch["target"]["product"] for patch in patchList if patch["target"] and patch["target"]["product"].startswith('KB')]
        if patches:
            print("[+] Asset ID : " + str(asset["id"]) + " | " + ", ".join(patches))
            assets_with_KB_patch_available[asset["id"]] = str(len(patches))

launch_script()
