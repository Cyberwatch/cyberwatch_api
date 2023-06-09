from cyberwatch_api import Cyberwatch_Pyhelper
from datetime import datetime, timedelta

##########################################
# VARIABLES À MODIFIER SELON LES BESOINS #
##########################################

ACTIF_ID = 1
MIN_CVSS_SCORE = 7

#########################################

def time_between(d1, d2):
    d1 = datetime.strptime(d1, '%Y-%m-%dT%H:%M:%S.%f%z')
    d2 = datetime.strptime(d2, '%Y-%m-%dT%H:%M:%S.%f%z')
    time_difference = d1 - d2
    if time_difference >= timedelta(hours=24):
        days = abs(time_difference.days)
        hours = int(abs(time_difference.seconds // 3600))
        return f"{days} jours et {hours} heures"
    else:
        hours = int(abs(time_difference.total_seconds() / 3600))
        return f"{hours} heures"

def format_date(d):
    date_object = datetime.strptime(d, '%Y-%m-%dT%H:%M:%S.%f%z')
    return date_object.strftime('%d %B %Y à %Hh%M')

def retrieve_actif_CVEs(actifID):
    """retrieve all CVE for a given actif"""
    apiResponse = Cyberwatch_Pyhelper().request(
        method="GET",
        endpoint="/api/v3/vulnerabilities/servers/" + str(actifID),
        verify_ssl= False,
    )
    return next(apiResponse).json()["cve_announcements"]

for res in retrieve_actif_CVEs(ACTIF_ID) :
    if res["score"] and res["score"] >= MIN_CVSS_SCORE:
        print(res["cve_code"] + " - Score : " + str(res["score"]))
        print("\tDétectée le : " + format_date(res["detected_at"]))

        if res["fixed_at"]:
            print("\tFixée le : " + format_date(res["fixed_at"]))
            print("\tTemps de résolution : " + str(time_between(res["fixed_at"], res["detected_at"])))
        else :
            print("\tFixée le : Jamais")
            print("\tTemps de résolution : Jamais")
        print("\n")