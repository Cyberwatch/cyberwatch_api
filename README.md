# Cyberwatch API

Python Api client for the Cyberwatch software
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents** 

- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Configuration](#configuration)
- [Ping](#ping)
- [Examples](#examples)
- [Usage](#usage)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->
## Installation

### Prerequisites
- [ ] [Python 3](https://www.python.org/)
- [ ] Python [PIP](https://pypi.org/project/pip/)

### Configuration

To be able to authenticate to the Cyberwatch API, you need to configure the api.conf file. This client authenticates using basic auth.

All the information can be retrieved in your profile on the Cyberwatch interface while creating an API user as following: 

"Profile > API keys > See my API keys > +Add"

You can download directly the api.conf file after clicking on "Create > Export" or copy/paste the information to an api.conf file in this directory.

## Ping

Create a ping.py script with the following content inside: 
```
from cyberwatch_api import Cyberwatch_Pyhelper

output = Cyberwatch_Pyhelper().request(
    method="get",
    endpoint="/api/v3/ping"
    )

print(next(output).json())
```

Then to test it, type the following command:

```bash
$ python3 ping.py
```

The output should look like this:
```bash
{"uuid": "1ab2c3de-546f-789g-9f87-6ed5c4b3a210"}
```
Otherwise, check that there are no typing errors in your API_KEY, SECRET_KEY or API_URL in the api.conf file and that your Cyberwatch instance is up.

## Examples

**Run an example script**

1. Choose a script from the examples directory and copy it to your computer

2. Run it with the following command:

```bash
$ python3 your_example_script_file.py
```

## Usage
**Swagger documentation**

Cyberwatch API provides a Swagger documentation.

Using it, you can :
 * Select the action you want to perform in the documentation
 * Update the "method", "endpoint" and parameters ("params") in you script according to the documentation 
 * Add any required logic

Note that the `request` method provided by this module always outputs a generator. This is intended to allow building of high performance scripts. If the request you perform returns a single result and not a list, you will find the result in the first row of this generator.

**Location of the Swagger's documentation**

You can find it while clicking on the </> logo on the top right of the Cyberwatch interface.
