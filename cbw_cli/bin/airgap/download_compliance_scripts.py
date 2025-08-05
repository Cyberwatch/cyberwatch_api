from os.path import abspath,  join
import os
from cbw_cli.bin import os as cbw_os
import argparse
import sys
import shutil

def help():
    print("Usage : cyberwatch-cli airgap download-scripts --os [KEY] --repositories [LIST]")
    print("---")
    print("Download compliance airgap scripts.\n")
    print("{: >20} \t {: >30} \t{}".format("ARGS", "DEFAULT", "DESCRIPTION"))
    print("{: >20} \t {: >30} \t{}".format("---", "---", "---"))
    print("{: >20} \t {: >30} \t{}".format("list-os", "-", "List all available operating systems"))
    print("{: >20} \t {: >30} \t{}".format("--os", "-", "Specify the target operating system"))
    print("{: >20} \t {: >30} \t{}".format("--repositories", "-", "Specify a list of repositories from which to gather the rules"))
    print("{: >20} \t {: >30} \t{}".format("--dest-dir", "cyberwatch-airgap-compliance", "Destination folder where to put the downloaded scripts"))
    print("\n")

def retrieve_compliance_scripts(os_key, repositories, CBW_API, verify_ssl=False):
    apiResponse = CBW_API.request(
        method="GET",
        endpoint="/api/v2/compliances/scripts",
        body_params={
            "os" : str(os_key),
            "repositories" : repositories
        },
        verify_ssl=verify_ssl
    )
    return next(apiResponse).json()

def download_compliance_scripts(os_key, repositories, destination_folder, CBW_API, verify_ssl=False):
    script_dir = join(abspath(destination_folder), "scripts")
    upload_dir = join(abspath(destination_folder), "uploads")
    if os.path.exists(script_dir):
        shutil.rmtree(script_dir)
    os.makedirs(script_dir, exist_ok=True)
    os.makedirs(upload_dir, exist_ok=True)

    print("Downloading compliance scripts..")
    compliance_scripts_metadata = retrieve_compliance_scripts(os_key, repositories, CBW_API, verify_ssl)

    if 'error' in compliance_scripts_metadata:
        print(compliance_scripts_metadata["error"]["message"])
        sys.exit(1)
    
    run_script = "".join((script_dir, "/", compliance_scripts_metadata["filename"]))
    with open(run_script, "w") as filestream:
        filestream.write(compliance_scripts_metadata["script_content"])
        os.chmod(run_script, 0o760)
    
    print("\033[A\033[A\nDownload complete ! Scripts are located in '" + str(destination_folder) + "'")
    

def manager(arguments, CBW_API, verify_ssl=False):

    parser = argparse.ArgumentParser()
    parser.add_argument("--os")
    parser.add_argument("--repositories", "--groups", nargs='*')
    parser.add_argument("--dest-dir", default="cyberwatch-airgap-compliance")
    parser.add_argument("help", nargs="?")
    options = parser.parse_args(arguments)

    if arguments and arguments[0] == "help":
        help()
    
    elif arguments and arguments[0] == 'list-os':
        cbw_os.manager(["list"], CBW_API)

    elif options.os is None or not options.repositories:
        print("You need to specify an OS and a list of one or many repositories to fetch the associated compliance rules.")
        print("--")
        print("Use the 'help' subcommand to view available actions")

    else:
        download_compliance_scripts(options.os, options.repositories, options.dest_dir, CBW_API, verify_ssl)
