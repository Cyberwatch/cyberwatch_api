#!/usr/bin/env python
# coding: utf-8


### This script analyzes patched CVE data to calculate key metrics, including the mean and median time to patch
### per year and overall. It also generates a CSV file detailing the impacted assets, associated
### CVEs, and the time taken to patch each vulnerability, providing a comprehensive overview of vulnerability management.

from cyberwatch_api import Cyberwatch_Pyhelper
from datetime import datetime, timedelta, timezone
import csv
import statistics


cbw = Cyberwatch_Pyhelper()


### Fetch all assets from Cyberwatch
def retrieve_assets():
    listAssets = []
    output = cbw.request(
        method="get",
        endpoint="/api/v3/servers?active=true&per_page=500"
    )

    for page in output: 
        listAssets.extend(page.json())
        print("\tAssets : {}".format(len(listAssets)), end='\r')
        
    print("")
    return listAssets


### Calculate time between to date
def time_between(d1, d2):
    d1 = datetime.strptime(d1, '%Y-%m-%dT%H:%M:%S.%f%z')
    d2 = datetime.strptime(d2, '%Y-%m-%dT%H:%M:%S.%f%z')
    timeDifference = d1 - d2
    return timeDifference.days

### Fetch CVE data from an asset
def retrieve_actif_CVEs(actifID):
    """retrieve all CVE for a given actif"""
    apiResponse = Cyberwatch_Pyhelper().request(
        method="GET",
        endpoint="/api/v3/vulnerabilities/servers/{}".format(actifID)
    )
    return next(apiResponse).json()["cve_announcements"]

print("")
print("Retrieve assets : ")
listAssets = retrieve_assets()


print("Retrieve CVE")

csvCve = [["Hostname","Asset id","CVE","Detected at","Fixed at","Resolution time (days)"]]
now = datetime.now(timezone.utc)
cvePerYear = {"last365d":[]}


# Loop through each asset to analyze all patched CVE
i = 0
for i, asset in enumerate(listAssets):

    print("Assets : {}/{}".format(i + 1,len(listAssets)), end='\r')
    cves = retrieve_actif_CVEs(asset["id"])

    # get only the patched CVE
    cvesFixed = [cve for cve in cves if cve['fixed_at'] is not None]

    if(not cvesFixed):
        continue


    for cveFixed in cvesFixed:
        cveTab = []
        timeToResolve = time_between(cveFixed["fixed_at"], cveFixed["detected_at"])

        cveTab.append(asset["hostname"])
        cveTab.append(asset["id"])
        cveTab.append(cveFixed["cve_code"])
        cveTab.append(cveFixed["detected_at"])
        cveTab.append(cveFixed["fixed_at"])
        cveTab.append(timeToResolve)

        fixed = datetime.strptime(cveFixed["fixed_at"],'%Y-%m-%dT%H:%M:%S.%f%z')

        # add the CVE data in the correct Year
        if (str(fixed.year) not in cvePerYear.keys()):
            cvePerYear[str(fixed.year)] = []
        cvePerYear[str(fixed.year)].append(timeToResolve)

        if ( (now - timedelta(days=365)) <= fixed <= now):
            cvePerYear["last365d"].append(timeToResolve)


        csvCve.append(cveTab)

print("Assets : {}/{}".format(i + 1,len(listAssets)), end='\r')

print("")

# Creation of the CSV file
path = "timeresolution.csv"
with open(path, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(csvCve)

print("CSV file created at {}".format(path))


# Print metrics
resolutionList = [] 

print("")
print("Stats per year :")
for fixedPerYear in sorted(cvePerYear.keys()):

    if(len(cvePerYear[fixedPerYear]) > 0):
        resolutionList.extend(cvePerYear[fixedPerYear])
        print("\tYear {} : Mean resolution time {} ; Median resolution Time {} ; Number of cve {}".format(fixedPerYear, statistics.mean(cvePerYear[fixedPerYear]), statistics.median(cvePerYear[fixedPerYear]), len(cvePerYear[fixedPerYear])))

if(len(resolutionList) > 0):
    print("")
    print("Stats global: Mean resolution time {} ; Median resolution Time {} ; Number of cve : {}".format(statistics.mean(resolutionList), statistics.median(resolutionList), len(resolutionList)))

