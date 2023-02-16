from cyberwatch_api import Cyberwatch_Pyhelper

output = Cyberwatch_Pyhelper().request(
    method="get",
    endpoint="/api/v3/assets/servers/{id}",
    params={'id' : 11453}
)

for res in output :
    print(res.json())
