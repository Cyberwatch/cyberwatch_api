# Cyberwatch Command Line Documentation

Cyberwatch's `cyberwatch-cli` command is Cyberwatch's command line interface. It allows you to interact with the API of your local instance, such as retrieving operating systems and managing airgap assets and compliance rules.

## Install `cyberwatch-cli`

The command line is installed as part of the [the classic installation
process](../README.md#installation) and will be added to your system's `PATH`. You can run the program directly from any command prompt or terminal.

## The syntax of `cyberwatch-cli`


The `cyberwatch-cli` command uses the following syntax:

```bash
cyberwatch-cli [COMMAND] [ARGUMENTS]
```

To discover the syntax of the `cyberwatch-cli` command, you can append the `help`  flag to any subcommand:

```bash
cyberwatch-cli help
cyberwatch-cli airgap download-scripts help
```

## Pass the configuration variables
The cyberwatch-cli command needs the variables `api-url`, `api-key` and `api-secret` to work properly. Several ways of transmitting these variables are supported.

### Through the command line

The syntax to pass the variables through the command line is:

```bash
cyberwatch-cli --api-url https://myinstance.local --api-key "PyXpxrcJ7rQ..." --api-secret "+bUx37WnB0qt..." [COMMAND] [ARGUMENTS]
```
### Through environnement variables

The variables can be set as environnement variables. You can use `api_url`, `api_key` and `api_secret`.

## Manage airgap assets

The command line interface can be used to download the scripts from the Cyberwatch instance, and upload the results of these scripts.

### Step 1: Download the scripts

You can download the scripts using this command below. If no directory is specified, this will create a default `cyberwatch-airgap` folder, relative to the current directory. 

```bash
cyberwatch-cli airgap download-scripts 
```

The scripts will be found in the `cyberwatch-airgap/scripts/` subfolder. To specify a different destination directory, you can use the `--dest-dir` argument.

```bash
export CYBERWATCH_DIR=/tmp/cyberwatch-airgap
cyberwatch-cli airgap download-scripts --dest-dir $CYBERWATCH_DIR
```

### Step 2: Execute the scripts

First, you need to copy the `cyberwatch-airgap/scripts/` folder on the machine you want to execute the scripts on. Then you can execute the scripts and direct the output to a specific file:

To execute the scripts on a Linux machine:

```bash
./cyberwatch-airgap/scripts/Linux/run > "cyberwatch-airgap/uploads/$(hostname)"
```

To execute the scripts on a Windows machine:

```bash
.\cyberwatch-airgap\scripts\Windows\run.ps1 > .\cyberwatch-airgap\uploads\${env:COMPUTERNAME}
```

### Step 3: Upload the result

To upload the results of the scripts:

```bash
cyberwatch-cli airgap upload
```
If no file is provided, the script tries to upload all the files present in `cyberwatch-airgap/uploads/`, relative to the current directory.

To manually provide the list of files to upload:

```bash
cyberwatch-cli airgap upload /tmp/cyberwatch-airgap/uploads/*
```

Once the upload is complete, the airgap asset will be available on your Cyberwatch instance.

## Manage airgap compliance rules

When an airgap asset is created, you can perform an airgap compliance scan and upload the result back to associate it to the asset.

### Step 1: Download the compliance rules

You can download the compliance rules by specifying the target operating system and a list of one or many repositories. If no directory is specified, this will create a default `cyberwatch-airgap-compliance` folder, relative to the current directory.

To list all operating systems available on your Cyberwatch instance:

```bash
cyberwatch-cli os list
```

To download the rules, you need to execute the following command and replace the `os` and `repositories` arguments with your own selected values, for example:

```bash
cyberwatch-cli airgap download-compliance-scripts --os ubuntu_2204_64 --repositories Security_Best_Practices CIS_Benchmark
```

The scripts will be found in the `cyberwatch-airgap-compliance/scripts/` subfolder. To specify a different destination directory, you can use the `--dest-dir` argument.

### Step 2: Execute the scripts

First, you need to copy the `cyberwatch-airgap-compliance/scripts/` folder on the machine you want to execute the scan on. Then you can execute the 'compliance' script and save the outputted result to a specific file:

To execute the scripts on a Linux machine:
```bash
./cyberwatch-airgap-compliance/scripts/compliance.sh > "cyberwatch-airgap-compliance/uploads/$(hostname)"
```

To execute the scripts on a Windows machine:
```bash
.\cyberwatch-airgap-compliance\scripts\compliance.ps1 > .\cyberwatch-airgap-compliance\uploads\${env:COMPUTERNAME}
```
### Step 3: Upload the result

To upload the result of the compliance scan:

```bash
cyberwatch-cli airgap upload-compliance
```
If no file is provided, the script tries to upload all the files available in `cyberwatch-airgap-compliance/uploads/`, relative to the current directory.

To manually provide the list of files to upload:

```bash
cyberwatch-cli airgap upload-compliance /tmp/cyberwatch-airgap-compliance/uploads/*
```

Once the upload is complete, the compliance analysis will be available on the asset's page.

## SSL Certificate Validation

By default, SSL certification validation is disabled, as most of the usage is performed locally on the Cyberwatch server. You can enable it by using the `--verify-ssl` flag, this makes sense in particular for remote usage:

```bash
cyberwatch-cli --verify-ssl os list
```
