from cyberwatch_api import Cyberwatch_Pyhelper

output = Cyberwatch_Pyhelper().request(
    method="post",
    endpoint="/api/v3/remote_accesses",
    body_params = {
  "type": "CbwRam::RemoteAccess::WinRm::WithNegotiate",
  "address": "AssetToSuperviseAdress",
  "port": 5985,
  "node_id": 1, #This can be found in the url of the node in the "Nodes" section of the Administration.
  "login": "YourLogin",
  "password": "TheCorrectPassWord"}
    )
print(next(output).json())

