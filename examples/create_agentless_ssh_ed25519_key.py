from cyberwatch_api import Cyberwatch_Pyhelper

output = Cyberwatch_Pyhelper().request(
    method="post",
    endpoint="/api/v3/remote_accesses",
    body_params = {
  "type": "CbwRam::RemoteAccess::Ssh::WithKey",
  "address": "AssetToSuperviseAdress",
  "port": 22,
  "node_id": 1, # This can be found in the node url in the "Nodes" section of the administration.
  "login": "YourLogin",
   #For the key don't forget to add "\n" between each line for a good Python interpretation
  "key" : "-----BEGIN OPENSSH PRIVATE KEY-----\nb3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW\nQyNTUxOQAAACB7DDf1EeFiOWQd89pjOKZD5rVgJNb00hBnahft16PEFwAAAJg8OsbVPDrG\n1QAAAAtzc2gtZWQyNTUxOQAAACB7DDf1EeFiOWQd89pjOKZD5rVgJNb00hBnahft16PEFw\nAAAEAklIdifS5obBkF5FKtOEWkbI+xB3Dm3RvZ66Vkt2bOo3sMN/UR4WI5ZB3z2mM4pkPm\ntWAk1vTSEGdqF+3Xo8QXAAAAEnVidW50dUBjYnctZGV2LXRtaQECAw==\n-----END OPENSSH PRIVATE KEY-----"}
    )
print(next(output).json())

