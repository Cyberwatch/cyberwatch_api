import sys
from cbw_cli.bin.airgap import download_scripts, download_compliance_scripts, upload_scripts, upload_compliance_scripts

def help():
    print("Usage : cyberwatch-cli airgap [COMMAND] [ARGS]")
    print("---")
    print("Import and Export airgap scripts and results.\n")
    print("{: >30} \t {}".format("COMMAND", "DESCRIPTION"))
    print("{: >30} \t {}".format("---", "---"))
    print("{: >30} \t {}".format("upload", "Upload airgap results"))
    print("{: >30} \t {}".format("upload-compliance", "Upload airgap compliance results"))
    print("{: >30} \t {}".format("download-scripts", "Download airgap scripts"))
    print("{: >30} \t {}".format("download-compliance-scripts", "Download airgap compliance scripts"))
    print("\n")

def manager(arguments, CBW_API, verify_ssl=False):
    if not arguments or arguments[0] == "help":
        help()

    elif arguments[0] == "download-scripts":
        download_scripts.manager(arguments[1:], CBW_API, verify_ssl)

    elif arguments[0] == "download-compliance-scripts":
        download_compliance_scripts.manager(arguments[1:], CBW_API, verify_ssl)

    elif arguments[0] == "upload":
        upload_scripts.manager(arguments[1:], CBW_API, verify_ssl)

    elif arguments[0] == "upload-compliance":
        upload_compliance_scripts.manager(arguments[1:], CBW_API, verify_ssl)

    else:
        print("ERROR : '" + str(arguments[0]) + "' is not a valid subcommand\n---", file=sys.stderr)
        help()
