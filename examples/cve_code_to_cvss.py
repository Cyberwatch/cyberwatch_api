"""
Script that expects a CVE code as an input and outputs its CVSSv3 string if it exists
"""

import sys
import itertools

from cyberwatch_api import Cyberwatch_Pyhelper

attacks_dict = {"access_vector": "AV", "access_complexity": "AC", "privileges_required": "PR",
    "user_interaction": "UI", "scope": "S", "confidentiality_impact": "C", "integrity_impact": "I",
    "availability_impact": "A", "exploit_code_maturity": "E"}
access_vector_dict = {"access_vector_network": "N", "access_vector_adjacent": "A",
                        "access_vector_local": "L", "access_vector_physical": "P"}
access_complexity_dict = {"access_complexity_low": "L", "access_complexity_high": "H"}
privileges_required_dict = {"privileges_required_none": "N", "privileges_required_low": "L",
"privileges_required_high": "H"}
user_interaction_dict = {"user_interaction_none": "N", "user_interaction_required": "R"}
scope_dict = {"scope_changed": "C", "scope_unchanged": "U"}
confidentiality_impact_dict = {"confidentiality_impact_high": "H",
"confidentiality_impact_low": "L", "confidentiality_impact_none": "N"}
integrity_impact_dict = {"integrity_impact_high": "H", "integrity_impact_low": "L",
                            "integrity_impact_none": "N"}
availability_impact_dict = {"availability_impact_high": "H", "availability_impact_low": "L",
                            "availability_impact_none": "N"}
exploit_code_maturity_dict = {"unproven": "U", "proof_of_concept": "P", "functional": "F",
                                "high": "H", "not_defined": "X"}

def retrieve_cvss_string(cve_code):
    """Requests Cyberwatch API to get details of the CVE
    Then build the CVSS string
    Returns 0 if sucessful
    Returns 1 if failed"""

    output = Cyberwatch_Pyhelper().request(
        method="get",
        endpoint=f"/api/v3/vulnerabilities/cve_announcements/{cve_code}",
        params = {"per_page": 100},
        verify_ssl=True
    )

    # Build the full CVSS dict
    full_cvss_dict = dict(itertools.chain(attacks_dict.items(), access_vector_dict.items(),
    access_complexity_dict.items(), privileges_required_dict.items(),
    user_interaction_dict.items(), scope_dict.items(), confidentiality_impact_dict.items(),
    integrity_impact_dict.items(), availability_impact_dict.items(),
    exploit_code_maturity_dict.items()))

    cve_details = next(output).json()
    cvss_v3_dict = cve_details["cvss_v3"]

    if cvss_v3_dict is None:
        return f"No CVSSv3 score for {cve_code}"

    # Append exploit code maturity infos to the dict from Cyberwatch
    if cve_details["exploit_code_maturity"] is not None:
        cvss_v3_dict["exploit_code_maturity"] = cve_details["exploit_code_maturity"]
    else:
        cvss_v3_dict["exploit_code_maturity"] = "not_defined"

    cvss_string = "CVSS:3.1/"
    for element in list(map(lambda x, y: full_cvss_dict[x]+":"+full_cvss_dict[y],
                         cvss_v3_dict.keys(), cvss_v3_dict.values())):
        cvss_string += element+"/"

    # Set values as Not Defined for Remediation Level and Report Confidence
    cvss_string += "RL:X/RC:X"
    return cvss_string

if __name__ == "__main__":
    retrieve_cvss_string(sys.argv[1])
