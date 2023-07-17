from cyberwatch_api import Cyberwatch_Pyhelper
from os.path import abspath, basename, dirname, join
from itertools import groupby
from .. import verify_ssl_value
import argparse
import chardet
import sys
import os

def help():
    print("Usage : ./" + str(sys.argv[0]) + " airgap upload [FILE1] [FILE2] [..]")
    print("---")
    print("Upload airgap compliance scan results.")
    print("---")
    print("If there is no file specified, this script will look into the `cyberwatch-airgap-compliance/uploads/` directory if it exists to find results scripts to upload.")

def upload_result_file(result_file):
    print("\n[*] Uploading : " + str(result_file))

    try: # Catch error like 'file doesn't exist'
        # Reading result file using detected encoding
        with open(result_file, "rb") as f:
            raw_content = f.read()
        file_content = raw_content.decode(chardet.detect(raw_content)["encoding"])
    except Exception as error:
        print(str(error))
        return

    # Sending result
    apiResponse = Cyberwatch_Pyhelper().request(
        method="POST",
        endpoint="/api/v2/cbw_scans/scripts",
        body_params={
            "output" : file_content
        },
        verify_ssl=verify_ssl_value()
    )
    result = next(apiResponse).json()

    # Printing the upload result
    if 'error' in result:
        print("ERROR : " + result["error"]["message"])
    elif 'server_id' in result:
        print("[+] Upload successful ! Server ID : " + str(result["server_id"]))
    else:
        print("Upload is done.")
        
    return next(apiResponse).json()

def manager(arguments):
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*")
    options = parser.parse_args(arguments)

    if arguments and arguments[0] == "help":
        help()
    
    elif not options.files:
        if not "cyberwatch-airgap-compliance" in os.listdir("."):
            help()
        else:
            print("No file has been specified, searching through the `cyberwatch-airgap-compliance/uploads/` directory.\n--")
            for file in os.listdir("cyberwatch-airgap-compliance/uploads"):
                upload_result_file(os.path.join("cyberwatch-airgap-compliance/uploads", file))
    else:
        for file in options.files:
            upload_result_file(file)

