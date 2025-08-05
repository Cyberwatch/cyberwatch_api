import argparse
import chardet
import os

def help():
    print("Usage : cyberwatch-cli airgap upload-compliance [FILE1] [FILE2] [..]")
    print("---")
    print("Upload airgap compliance scan results.")
    print("---")
    print("If there is no file specified, this script will look into the `cyberwatch-airgap-compliance/uploads/` directory if it exists to find results scripts to upload.")

def upload_result_file(result_file, CBW_API, verify_ssl=False):
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
    apiResponse = CBW_API.request(
        method="POST",
        endpoint="/api/v2/compliances/scripts",
        body_params={
            "output" : file_content
        },
        timeout=90,
        verify_ssl=verify_ssl
    )
    # If the operation is successful, the apiResponse is empty and the status code is 204
    # Else, an error is reported with a status code != 204
    result = next(apiResponse)

    if result.status_code == 204:
        print("Upload is successful.")
    else:
        print("ERROR : " + str(result.content))

def manager(arguments, CBW_API, verify_ssl=False):

    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*")
    options = parser.parse_args(arguments)

    if arguments and arguments[0] == "help":
        help()
    
    elif not options.files:
        if "cyberwatch-airgap-compliance" not in os.listdir("."):
            help()
        else:
            print("No file has been specified, searching through the `cyberwatch-airgap-compliance/uploads/` directory.\n--")
            for file in os.listdir("cyberwatch-airgap-compliance/uploads"):
                upload_result_file(os.path.join("cyberwatch-airgap-compliance/uploads", file), CBW_API, verify_ssl)
    else:
        for file in options.files:
            upload_result_file(file, CBW_API, verify_ssl)

