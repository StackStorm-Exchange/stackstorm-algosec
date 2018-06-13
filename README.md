[![Build Status](https://circleci.com/gh/EncoreTechnologies/stackstorm-algosec.svg?style=shield&circle-token=:circle-token)](https://circleci.com/gh/EncoreTechnologies/stackstorm-algosec) [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# AlgoSec Integration Pack

# <a name="Introduction"></a> Introduction

This pack provides integration with the AlgoSec Firewall Analyzer and FireFlow SOAP API.
Actions within this back mirror one-for-one the "commands" in the SOAP API
Data types and payloads also mirror one-for-one.

# <a name="QuickStart"></a> Quick Start

1. Install the pack

    ``` shell
    st2 pack install menandmice
    ```

2. Execute an action (example: list all DNS Zones)

    ``` shell
    st2 run algosec.afa_connect server=algosec.domain.tld username=administrator password=xxx

# <a name="Configuration"></a> Configuration

The configuration for this pack is used to specify connection information for
all AlgoSec servers you'll be communicating with. The location for the config file
is `/opt/stackstorm/config/algosec.yaml`.


**Note** : `st2 pack config` doesn't handle schemas refernences very well (known bug)
    so it's best to create the configuraiton file yourself and copy it into
    `/opt/stackstorm/configs/algosec.yaml` then run `st2ctl reload --register-configs`

## <a name="Schema"></a> Schema

``` yaml
---
algosec:
  <connection-name-1>:
    server: <hostname or ip of the AlgoSec server>
    username: <username@domain.tld (preferred) or domain\username>
    password: <password for username>
  <connection-name-2>:
    server: <hostname or ip of the AlgoSec server>
    username: <username@domain.tld (preferred) or domain\username>
    password: <password for username>
    port: <port number override to use for the connections: default = None (defaults to 80/443)>
    transport: <transport override to use for the connections: default = http'>
    wsdl_endpoint: <HTTP URL for the algosec WSDL: default = 'AFA/php/ws.php?wsdl'>
  <connection-name-3>:
    ... # note: multiple connections can be specified!
```

## <a name="SchemaExample"></a> Schema Examples

``` yaml
---
algosec:
  dev:
    server: algosec.dev.domain.tld
    username: stackstorm_svc@dev.domain.tld
    password: DevPassword
  stage:
    server: algosec.stage.domain.tld
    username: stackstorm_svc@stage.domain.tld
    password: stagePassword
    port: 8080
  prod:
    server: algosec.prod.domain.tld
    username: stackstorm_svc@prod.domain.tld
    password: SuperSecret
    transport: https
```

**Note** : All actions allow you to specify a `connection` name parameter that will
           reference the conneciton information in the config. Alternatively
           all actions allow you to override these connection parameters
           so a config isn't required. See the [Actions](#Actions) for more
           information.

# Actions

Actions in this pack are auto-generated from the AlgoSec SOAP API operations defined in the WSDL file
(note: we store these WSDLs in the `etc/` directory of this pack). There is
an action created for every "Command" in the AlgoSec API. Input and output
parameters should be the same with all action names and action parameters
convert from CamelCase to snake_case with a few expecptions. Example: SOAP command IsSessionAlive
will be converted to snake_case for the action to become `algosec.is_session_alive`.
In this same command one of the arguments is `SessionID` that becomes the
`session_id` action parameter.


## <a name="UsageBasic"></a> Usage - Basic

The following example demonstrates running the `menandmice.get_dns_zones` action
using connection information specified as action input parameters.

``` shell
$ st2 run algosec.afa_connect server="algosec.dev.domain.tld" username="admin" password="xxx"
...
id: 5b1eb8fbef13d85d6d0300a7
status: succeeded
parameters:
  password: '********'
  server: algosec.dev.domain.tld
  username: admin
result:
  exit_code: 0
  result:
    session_id: 3ae118bd61c30ed35998c4b4b39c11ff
  stderr: ''
  stdout: ''
```

The basic example is great and allows for quick testing from the commandline and/or
one-off commands in a workflow. However, specifying the same connection information
over/over can become tedious and repetitive, luckyily there is a better way.


## <a name="UsageConfig"></a> Usage - Config Connection

This pack is designed to store commonly used connection information in the pack's
config file located in `/opt/stackstorm/config/algosec.yaml`. The connection
info is specified in the config once, and then referenced by name within an
action and/or workflow.

Using the action from the basic example, we can enter this connection information
in our config:

``` shell
$ cat /opt/stackstorm/configs/algosec.yaml
---
algosec:
  dev:
    server: algosec.dev.domain.tld
    username: admin
    password: xxx
```

Now we can reference this connection (by name) when executing our action:

``` shell
$ st2 run algosec.afa_connect connection=dev
..
id: 5b1ec42def13d85d6d03022c
status: succeeded
parameters:
  connection: dev
result:
  exit_code: 0
  result:
    session_id: a4593c231ec037e621239ffbeb2e3cfe
  stderr: ''
  stdout: ''
```

This pays off big time when running multiple commands in sequence.

# Version Compatiblity

| Pack Version | AlgoSec Version |
|--------------|-----------------|
| 0.1.0        | v2017.3         |

# Future
- Implement business flow actions
