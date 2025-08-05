from os.path import abspath, basename, dirname, join
from itertools import groupby
import argparse
import os
import requests

def help():
    print("Usage : cyberwatch-cli airgap download-scripts [ARGS]")
    print("---")
    print("Download airgap scripts.\n")
    print("{: >23} \t {: >20} \t{}".format("ARGS", "DEFAULT", "DESCRIPTION"))
    print("{: >23} \t {: >20} \t{}".format("---", "---", "---"))
    print("{: >23} \t {: >20} \t{}".format("--add-attachment", "False", "Download the Windows cab file"))
    print("{: >23} \t {: >20} \t{}".format("--dest-dir", "cyberwatch-airgap", "Destination folder where to put the downloaded scripts"))
    print("\n")

SH_EXECUTE_SCRIPT = """#!/bin/bash
set -eu
readonly DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" &> /dev/null && pwd )"
for script in {}; do
    script=$DIR/$script
    chmod +x "$script"
    >&2 printf "Executing %s..." "$script"
    ( "$script" || >&2 echo "Error" ; ) && >&2 echo "Done"
done
"""

def retrieve_scripts(scriptID, CBW_API, verify_ssl=False):
    # If the script ID is an empty string, this will fetch every scripts available
    apiResponse = CBW_API.request(
        method="GET",
        endpoint="/api/v2/cbw_scans/scripts/" + str(scriptID),
        verify_ssl=verify_ssl
    )
    return next(apiResponse).json()

def download_scripts(destination_folder, CBW_API, verify_ssl=False, with_attachment=False):
    script_dir = join(abspath(destination_folder), "scripts")
    upload_dir = join(abspath(destination_folder), "uploads")
    os.makedirs(script_dir, exist_ok=True)
    os.makedirs(upload_dir, exist_ok=True)

    scripts_metadata = retrieve_scripts("", CBW_API, verify_ssl)
    print("Downloading scripts..")
    # Downloading every single script
    saved_scripts = [download_individual_script(script["id"], script_dir, CBW_API, with_attachment, verify_ssl) for script in scripts_metadata]
    # Grouping script by OS
    grouped_scripts = groupby(sorted(saved_scripts), lambda x: x[0])

    # For each OS, create the 'run' root script 
    for target_os, scripts in grouped_scripts:

        if target_os in ("Aix", "Linux", "Macos", "Vmware"):
            run_script_filename = join(script_dir, target_os, "run")
            with open(run_script_filename, "w") as file_stream:
                file_stream.write(SH_EXECUTE_SCRIPT.format(" ".join(sorted([content for (os, content) in scripts], key=lambda x: (x[0] != 'I', x)))))
                os.chmod(run_script_filename, 0o760)

        if target_os == "Windows":
                run_script_filename = join(script_dir, target_os, "run.ps1")
                with open(run_script_filename, "w") as file_stream:
                    file_stream.write("$ScriptDir = Split-Path $MyInvocation.MyCommand.Path\n")
                    for _, script in scripts:
                        file_stream.write(f'& "$ScriptDir/{script}"\n')
        
        print("\033[A\033[A\nDownload complete ! Scripts are located in '" + str(destination_folder) + "'" + " " * 20)

def append_extension(target_os):
    if target_os in ("Aix", "Linux", "Macos", "Vmware"):
        return ".sh"
    if target_os == "Windows":
        return ".ps1"
    return ""

def download_individual_script(scriptID, base_dir, CBW_API, with_attachment=False, verify_ssl=False):
    script = retrieve_scripts(str(scriptID), CBW_API, verify_ssl)
    if script is None or script["type"] is None:
        return None, None

    target_os, script_name = script["type"].split("::")[1:]
    script_dir = join(base_dir + "/" + target_os)
    script_filename = script_name + append_extension(target_os)

    # Save the script in the correct directory
    os.makedirs(dirname(join(script_dir, script_filename)), exist_ok=True)
    with open(join(script_dir, script_filename), "w") as scriptFile:
        scriptFile.write(script["contents"])

    # Download the attachment if it exists
    if script["attachment"] and with_attachment:
        attachment = requests.get(script["attachment"], allow_redirects=True, verify=verify_ssl)
        with open(join(script_dir, basename(script["attachment"])), "wb") as attachmentFile:
            attachmentFile.write(attachment.content)

    print("\033[A\033[A\nDownloaded script : " + str(script_name) + " " * 40)
    return target_os, script_filename

def manager(arguments, CBW_API, verify_ssl=False):

    parser = argparse.ArgumentParser()
    parser.add_argument("--add-attachment", action="store_true")
    parser.add_argument("--dest-dir", default="cyberwatch-airgap")
    parser.add_argument("help", nargs="?")
    options = parser.parse_args(arguments)

    if arguments and arguments[0] == "help":
        help()
    else:
        download_scripts(options.dest_dir, CBW_API, verify_ssl, options.add_attachment)
