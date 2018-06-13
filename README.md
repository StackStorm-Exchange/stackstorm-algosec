[![Build Status](https://circleci.com/gh/EncoreTechnologies/stackstorm-algosec.svg?style=shield&circle-token=:circle-token)](https://circleci.com/gh/EncoreTechnologies/stackstorm-algosec) [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# AlgoSec Integration Pack

# <a name="Introduction"></a> Introduction

This pack provides integration with the AlgoSec Firewall Analyzer and FireFlow SOAP API.
Actions within this back mirror one-for-one the "commands" in the SOAP API
Data types and payloads also mirror one-for-one.

# <a name="QuickStart"></a> Quick Start

1. Install the pack

    ``` shell
    st2 pack install algosec
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

**Note**: that there are currently issues with the some of the AlgoSec AFA Actions not returning informaiton in the proper formats. Currently working with the vendor to fix.

| Reference of the Action | Description |
|-------------------------|-------------|
| algosec.fireflow_delete_object_custom_field | Invokes the AlgoSec SOAP command deleteObjectCustomField |
| algosec.fireflow_authenticate | Invokes the AlgoSec SOAP command authenticate |
| algosec.fireflow_create_ticket | Invokes the AlgoSec SOAP command createTicket |
| algosec.fireflow_get_template_fields | Invokes the AlgoSec SOAP command getTemplateFields |
| algosec.fireflow_get_ticket | Invokes the AlgoSec SOAP command getTicket |
| algosec.fireflow_is_session_alive | Invokes the AlgoSec SOAP command isSessionAlive |
| algosec.fireflow_get_fields | Invokes the AlgoSec SOAP command getFields |
| algosec.fireflow_add_object_custom_field | Invokes the AlgoSec SOAP command addObjectCustomField |
| algosec.fireflow_update_object_custom_field | Invokes the AlgoSec SOAP command updateObjectCustomField |
| algosec.afa_create_role | Invokes the AlgoSec SOAP command create_role |
| algosec.afa_create_device_group | Invokes the AlgoSec SOAP command create_device_group |
| algosec.afa_delete_scheduler_job | Invokes the AlgoSec SOAP command delete_scheduler_job |
| algosec.afa_get_hostgroups_by_device | Invokes the AlgoSec SOAP command get_hostgroups_by_device |
| algosec.afa_get_unused_rules | Invokes the AlgoSec SOAP command get_unused_rules |
| algosec.afa_get_entity_id | Invokes the AlgoSec SOAP command get_entity_id |
| algosec.afa_import_risks_from_spreadsheet | Invokes the AlgoSec SOAP command import_risks_from_spreadsheet |
| algosec.afa_delete_user | Invokes the AlgoSec SOAP command delete_user |
| algosec.afa_get_all_hostgroups | Invokes the AlgoSec SOAP command get_all_hostgroups |
| algosec.afa_get_rule_documentation | Invokes the AlgoSec SOAP command get_rule_documentation |
| algosec.afa_create_user | Invokes the AlgoSec SOAP command create_user |
| algosec.afa_connect | Invokes the AlgoSec SOAP command connect |
| algosec.afa_query | Invokes the AlgoSec SOAP command query |
| algosec.afa_set_configuration | Invokes the AlgoSec SOAP command set_configuration |
| algosec.afa_set_scheduler_job | Invokes the AlgoSec SOAP command set_scheduler_job |
| algosec.afa_get_groups_list | Invokes the AlgoSec SOAP command get_groups_list |
| algosec.afa_disconnect | Invokes the AlgoSec SOAP command disconnect |
| algosec.afa_search_object_by_ip | Invokes the AlgoSec SOAP command search_object_by_ip |
| algosec.afa_get_configuration | Invokes the AlgoSec SOAP command get_configuration |
| algosec.afa_delete_role | Invokes the AlgoSec SOAP command delete_role |
| algosec.afa_device_changes_over_time_report | Invokes the AlgoSec SOAP command device_changes_over_time_report |
| algosec.afa_get_members_by_device | Invokes the AlgoSec SOAP command get_members_by_device |
| algosec.afa_update_user | Invokes the AlgoSec SOAP command update_user |
| algosec.afa_get_all_services | Invokes the AlgoSec SOAP command get_all_services |
| algosec.afa_get_report_pdf | Invokes the AlgoSec SOAP command get_report_pdf |
| algosec.afa_add_device_to_group | Invokes the AlgoSec SOAP command add_device_to_group |
| algosec.afa_get_group_content | Invokes the AlgoSec SOAP command get_group_content |
| algosec.afa_is_session_alive | Invokes the AlgoSec SOAP command is_session_alive |
| algosec.afa_get_nat_discovery | Invokes the AlgoSec SOAP command get_nat_discovery |
| algosec.afa_get_rules_by_device | Invokes the AlgoSec SOAP command get_rules_by_device |
| algosec.afa_import_risks_from_xml | Invokes the AlgoSec SOAP command import_risks_from_xml |
| algosec.afa_risks_summary | Invokes the AlgoSec SOAP command risks_summary |
| algosec.afa_get_containing_objects | Invokes the AlgoSec SOAP command get_containing_objects |
| algosec.afa_get_hostgroup_by_name_and_device | Invokes the AlgoSec SOAP command get_hostgroup_by_name_and_device |
| algosec.afa_create_domain | Invokes the AlgoSec SOAP command create_domain |
| algosec.afa_get_entity_name | Invokes the AlgoSec SOAP command get_entity_name |
| algosec.afa_create_device | Invokes the AlgoSec SOAP command create_device |
| algosec.afa_get_devices_list | Invokes the AlgoSec SOAP command get_devices_list |
| algosec.afa_get_services_by_device | Invokes the AlgoSec SOAP command get_services_by_device |
| algosec.afa_get_parent_device | Invokes the AlgoSec SOAP command get_parent_device |
| algosec.afa_delete_device | Invokes the AlgoSec SOAP command delete_device |
| algosec.afa_start_analysis | Invokes the AlgoSec SOAP command start_analysis |
| algosec.afa_get_device_statistics | Invokes the AlgoSec SOAP command get_device_statistics |
| algosec.afa_update_role | Invokes the AlgoSec SOAP command update_role |
| algosec.afa_edit_rule_documentation | Invokes the AlgoSec SOAP command edit_rule_documentation |
| algosec.afa_get_license | Invokes the AlgoSec SOAP command get_license |
| algosec.afa_search_rule | Invokes the AlgoSec SOAP command search_rule |
| algosec.afa_get_service_by_name_and_device | Invokes the AlgoSec SOAP command get_service_by_name_and_device |

## <a name="UsageBasic"></a> Usage - Basic

The following example demonstrates running the `algosec.afa_connect` action
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
