#!/usr/bin/env python3

"""Remove assets on a cyberwatch instance based on the number of days of the last communication.
"""

from datetime import datetime, timedelta
from cyberwatch_api import Cyberwatch_Pyhelper

def get_assets():
    """Get all assets for a cyberwatch instance."""
    assets = []
    apiResponse = Cyberwatch_Pyhelper().request(
        method="GET",
        endpoint="/api/v3/servers",
    )
    for page in apiResponse:
        assets = assets + page.json()

    return assets

def filter_assets_last_communication(assets: list[dict], days: int) -> list[dict]:
    """Filter a list of asset with the number of days since last communication."""
    time_now = datetime.now()
    filtered_assets = []

    for asset in assets:
        last_communication_datetime = datetime.strptime(asset["last_communication"], "%Y-%m-%dT%H:%M:%S.%f%z").replace(tzinfo=None)
        # Compute the delta between now and the last communication of the asset.
        # If the delta is greater than the given number of days, it is included in the list of assets to be deleted.
        if time_now - last_communication_datetime > timedelta(days=days):
            filtered_assets.append(asset)
    return filtered_assets

def delete_assets(assets: list[dict]) -> None:
    """Delete the assets for a cyberwatch instance."""
    for asset in assets:
        Cyberwatch_Pyhelper().request(
                method="delete",
                endpoint=f"/api/v3/assets/servers/{asset['id']}",
                verify_ssl=False
        )

if __name__ == "__main__":
    assets = get_assets()
    print(f"Got {len(assets)} total assets")
    assets = filter_assets_last_communication(assets=assets, days=30)  # Remove assets that did not communicate during the last 30 days
    delete_assets(assets)
    print(f"Delete {len(assets)} assets")
