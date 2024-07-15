import argparse
import chardet
import os

def help():
    print("Usage : cyberwatch-cli airgap upload [FILE1] [FILE2] [..]")
    print("---")
    print("Upload airgap scan results.")
    print("---")
    print("If there is no file specified, this script will look into the `cyberwatch-airgap/uploads/` directory if it exists to find results scripts to upload.")

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
        endpoint="/api/v2/cbw_scans/scripts",
        body_params={
            "output" : file_content
        },
        timeout=90,
        verify_ssl=verify_ssl
    )
    result = next(apiResponse).json()

    # Printing the upload result
    if 'error' in result:
        print("ERROR : " + result["error"]["message"])
    elif 'server_id' in result:
        print("[+] Upload successful ! Server ID : " + str(result["server_id"]))
    else:
        print("Upload is done.")

    return result

def manager(arguments, CBW_API, verify_ssl=False):

    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*")
    options = parser.parse_args(arguments)

    if arguments and arguments[0] == "help":
        help()
    
    elif not options.files:
        if "cyberwatch-airgap" not in os.listdir("."):
            help()
        else:
            print("No file has been specified, searching through the `cyberwatch-airgap/uploads/` directory.\n--")
            for file in os.listdir("cyberwatch-airgap/uploads"):
                upload_result_file(os.path.join("cyberwatch-airgap/uploads", file), CBW_API, verify_ssl)
    else:
        for file in options.files:
            upload_result_file(file, CBW_API, verify_ssl)
