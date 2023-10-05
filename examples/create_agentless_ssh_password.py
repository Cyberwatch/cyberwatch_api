from cyberwatch_api import Cyberwatch_Pyhelper

output = Cyberwatch_Pyhelper().request(
    method="post",
    endpoint="/api/v3/remote_accesses",
    body_params = {
  "type": "CbwRam::RemoteAccess::Ssh::WithPassword",
  "address": "AssetToSuperviseAdress",
  "port": 22,
  "node_id": 1, #This can be found in the node url in the "Nodes" section of the administration.
  "login": "YourLogin",
  "password": "YouPassword"}
    )

print(next(output).json())

