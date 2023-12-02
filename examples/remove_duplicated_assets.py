"""
Script used to remove duplicated assets from your Cyberwatch instance.
In default mode, the script will not delete assets automatically,
it will just display the assets that would be removed if executed in delete mode.
"""

from cyberwatch_api import Cyberwatch_Pyhelper

def find_duplicates(servers_list):
    '''Find duplicated servers'''
    sorted_servers = sorted(servers_list, key=lambda x: (x["hostname"] is None, x["hostname"]))
    previous_server = sorted_servers[0]
    duplicates_list = []

    for server in sorted_servers[1:]:
        if server["hostname"] == previous_server["hostname"] and server["hostname"] is not None:
            if previous_server["last_communication"] is None and server["last_communication"] is not None:
                duplicates_list.append(previous_server)
            elif server["last_communication"] is None or\
                previous_server["last_communication"] > server["last_communication"]:
                duplicates_list.append(server)
            else:
                duplicates_list.append(previous_server)
                previous_server = server
        else:
            previous_server = server

    return duplicates_list

def display_and_delete(dups, delete=False):
    '''Display servers and delete them if asked for'''
    print(f"\n\n================= Total of {len(dups)} assets\
 to delete (delete={delete}) =================")

    for delete_server in dups:
        print(f"id: {delete_server['id']} --- hostname: {delete_server['hostname']} ---\
 creation date: {delete_server['created_at']}")

        if delete is True:
            next(Cyberwatch_Pyhelper().request(
                method="delete",
                endpoint=f"/api/v3/assets/servers/{delete_server['id']}",
                verify_ssl=False
            ))

def retrieve_assets():
    """retrieve all assets for a cyberwatch node"""
    assets = []
    apiResponse = Cyberwatch_Pyhelper().request(
        method="GET",
        endpoint="/api/v3/assets/servers",
        verify_ssl=False
    )
    print("Retrieving assets : 0")
    for page in apiResponse:
        assets = assets + page.json()
        print("\033[A\033[A\nRetrieving assets : " + str(len(assets)))
    return assets

if __name__ == "__main__":

    duplicates = find_duplicates(retrieve_assets())
    display_and_delete(duplicates, delete=False)
