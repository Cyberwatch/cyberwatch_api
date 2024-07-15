from cyberwatch_api import Cyberwatch_Pyhelper

"""
This script will fetch all the rules associated to the repository list defined, and 
assign to them either all Windows 10 or Windows 11 OS according to the user choice.
"""

####################
# Script variables #
####################

REPOSITORIES = ["Security_Best_Practices"]
WINDOWS_VERSION = 10 # Can either be '10' or '11'

####################

def retrieve_os():
    apiResponse = Cyberwatch_Pyhelper().request(
        method="GET",
        endpoint="/api/v3/os",
        verify_ssl=False
    )
    os = []
    for page in apiResponse: 
        os = os + page.json()
    return os

def repository_rules(repositories):
    """retrieve all available patches for a given asset"""
    apiResponse = Cyberwatch_Pyhelper().request(
        method="GET",
        endpoint="/api/v3/rules",
        body_params={
            "repositories" : repositories,
        },
        verify_ssl=False
    )
    rules=[]
    print("Retrieving rules : 0")
    for page in apiResponse: 
        rules = rules + page.json()
        print("\033[A\033[A\nRetrieving rules : " + str(len(rules)) + "\n")
    return rules

def update_rule(ruleID, os_groups):
    apiResponse = Cyberwatch_Pyhelper().request(
        method="PUT",
        endpoint="/api/v3/rules/" + str(ruleID),
        body_params={
            "os": os_groups
        },
        verify_ssl=False
    )
    return next(apiResponse).json()

def launch_script():
    # Retrieve all compliance rules associated to the repositories we set
    compliance_rules = repository_rules(REPOSITORIES)
    # Retrieve all Windows OS keys according to the WINDOWS_VERSION variable
    windows_os = [windows["key"] for windows in retrieve_os() if windows["key"].lower().startswith("windows_" + str(WINDOWS_VERSION))]
    
    for index, rule in enumerate(compliance_rules):
        rule_current_os = [os["key"] for os in rule["os"]] # Get current OS the rule is applied to
        new_rule_os = list(set(rule_current_os + windows_os)) # Add the windows OS to the already existing OS

        print("\033[A\033[A")
        print("Updating rule : " + str(index + 1) + " / " + str(len(compliance_rules)))

        update_rule(rule["id"], new_rule_os)

launch_script()
