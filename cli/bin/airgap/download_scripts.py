from cyberwatch_api import Cyberwatch_Pyhelper
from os.path import abspath, basename, dirname, join
from itertools import groupby
from .. import verify_ssl_value
import argparse
import sys
import os
import requests

def help():
    print("Usage : " + str(sys.argv[0]) + " airgap download-scripts [ARGS]")
    print("---")
    print("Download airgap scripts.\n")
    print("{: >23} \t {: >20} \t{}".format("ARGS", "DEFAULT", "DESCRIPTION"))
    print("{: >23} \t {: >20} \t{}".format("---", "---", "---"))
    print("{: >23} \t {: >20} \t{}".format("--no-attachement", "False", "-"))
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

def retrieve_scripts(scriptID=""):
    apiResponse = Cyberwatch_Pyhelper().request(
        method="GET",
        endpoint="/api/v2/cbw_scans/scripts/" + str(scriptID),
        verify_ssl=verify_ssl_value()
    )
    return next(apiResponse).json()

def download_scripts(destination_folder, with_attachment=False):
    script_dir = join(abspath(destination_folder), "scripts")
    upload_dir = join(abspath(destination_folder), "uploads")
    os.makedirs(script_dir, exist_ok=True)
    os.makedirs(upload_dir, exist_ok=True)

    scripts_metadata = retrieve_scripts()
    print("Downloading scripts..")
    # Downloading every single script
    saved_scripts = [download_individual_script(script["id"], script_dir, with_attachment) for script in scripts_metadata]
    # Grouping script by OS
    grouped_scripts = groupby(sorted(saved_scripts), lambda x: x[0])

    # For each OS, create the 'run' root script 
    for target_os, scripts in grouped_scripts:

        if target_os in ("Aix", "Linux", "Macos", "Vmware"):
            run_script_filename = join(script_dir, target_os, "run")
            with open(run_script_filename, "w") as file_stream:
                file_stream.write(SH_EXECUTE_SCRIPT.format(" ".join(content for (os, content) in scripts)))
                os.chmod(run_script_filename, 0o755)

        if target_os == "Windows":
                run_script_filename = join(script_dir, target_os, "run.ps1")
                with open(run_script_filename, "w") as file_stream:
                    file_stream.write("$ScriptDir = Split-Path $MyInvocation.MyCommand.Path\n")
                    for _, script in scripts:
                        file_stream.write(f'& "$ScriptDir/{script}"\n')
        
        print("\033[A\033[A\nDownload complete ! Scripts are located in '" + str(destination_folder) + "'" + " " * 20)

def append_extension(target_os):
    if target_os in ("Aix", "Linux", "Macos", "Vmware"): return ".sh"
    if target_os == "Windows": return ".ps1"
    return ""

def download_individual_script(scriptID, base_dir, with_attachment=False):
    script = retrieve_scripts(str(scriptID))
    if script is None or script["type"] is None: return None, None

    target_os, script_name = script["type"].split("::")[1:]
    script_dir = join(base_dir + "/" + target_os)
    script_filename = script_name + append_extension(target_os)

    # Save the script in the correct directory
    os.makedirs(dirname(join(script_dir, script_filename)), exist_ok=True)
    with open(join(script_dir, script_filename), "w") as scriptFile:
        scriptFile.write(script["contents"])

    # Download the attachment if it exists
    if script["attachment"] and with_attachment:
        attachment = requests.get(script["attachment"], allow_redirects=True, verify=False)
        with open(join(script_dir, basename(script["attachment"])), "wb") as attachmentFile:
            attachmentFile.write(attachment.content)

    print("\033[A\033[A\nDownloaded script : " + str(script_name) + " " * 40)
    return target_os, script_filename

def manager(arguments):
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-attachment", action="store_false")
    parser.add_argument("--dest-dir", default="cyberwatch-airgap")
    parser.add_argument("help", nargs="?")
    options = parser.parse_args(arguments)

    if arguments and arguments[0] == "help":
        help()
    else:
        download_scripts(options.dest_dir, options.no_attachment)
