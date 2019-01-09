#!/usr/bin/env python
#
# Description:
#
# Usage:
#
# Files generated
#  actions/*.yaml (one for each operation in etc/algosec_wsdl.xml)
#

import argparse
import datetime
import glob
import jinja2
import json
import os
import re
import requests
from xml.dom import minidom
import yaml
import zeep
from operator import itemgetter


ACTION_TEMPLATE_PATH = "./action_template.yaml.j2"
ACTION_INFORMATION_PATH = "./action_information.md.j2"
ACTION_DIRECTORY = "../actions"
README_PATH = "../README.md"
API_ENDPOINTS = [
    {'NAME': "fireflow",
    "WSDL_ENDPOINT": "WebServices/FireFlow.wsdl",
    "WSDL_GLOB_PATH": "./fireflow_wsdl_*.xml"},
    {'NAME': "afa",
    "WSDL_ENDPOINT": "AFA/php/ws.php?wsdl",
    "WSDL_GLOB_PATH": "./afa_wsdl_*.xml"},
]


class Cli:
    def parse(self):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        # Subparsers
        subparsers = parser.add_subparsers(dest="command")

        # commands
        fetch_parser = subparsers.add_parser('fetch-wsdl',
                                             help="Deploy packs to a host")
        # connection args
        fetch_parser.add_argument('-H', '--hostname',
                                  help='Hostname/IP of AlgoSec Server',
                                  required=True)
        fetch_parser.add_argument('-w', '--wsdl-path',
                                  help="WSDL file to write to")

        generate_parser = subparsers.add_parser('generate',
                                                help="Generate actions from the the WSDL")
        action_dir = os.path.join(os.path.dirname(__file__), '..', 'actions')
        generate_parser.add_argument('-d', '--directory', default=action_dir,
                                     help="Directory where actions should be written to")
        generate_parser.add_argument('-w', '--wsdl-path',
                                     help="WSDL file to use")

        subparsers.add_parser('examples',
                              help="Prints examples of how to use this script to stdout")

        args = parser.parse_args()
        if args.command == "examples":
            self.examples()
            exit(0)
        return args

    def examples(self):
        print("examples:\n"
            "  # fetch the latest WSDL from the AlgoSec server/\n"
            "  ./action_generate.py fetch-wsdl -H host.domain.tld\n"
            "\n"
            "  # fetch the latest WSDL from the AlgoSec server to a specific name/\n"
            "  ./action_generate.py fetch-wsdl -H host.domain.tld -w algosec_wsdl_new.xml\n"
            "\n"
            "  # gerenate actions from the latest WSDL/\n"
            "  ./action_generate.py generate\n"
            "\n"
            "  # gerenate actions into an alternate directory from a specific WSDL/\n"
            "  ./action_generate.py generate -d ../actions_new -w algosec_wsdl_new.xml\n")


class ActionGenerator(object):

    def __init__(self, cli_args, **kwargs):
        self.cli_args = cli_args
        self.action_template_params = self.load_template_params()

    def load_template_params(self):
        params_yaml_str = self.jinja_render_file(ACTION_TEMPLATE_PATH,
                                                 {'operation_camel_case': ''})
        params_dict = yaml.load(params_yaml_str)
        params = params_dict['parameters'].keys()
        return params

    def fetch_wsdl(self):
        for wsdl in API_ENDPOINTS:
            wsdl_url = "https://{0}/{1}".format(self.cli_args.hostname, wsdl['WSDL_ENDPOINT'])
            response = None
            try:
                response = requests.get(wsdl_url)
            except requests.exceptions.SSLError:
                response = requests.get(wsdl_url, verify=False)

            xml = minidom.parseString(response.text)
            xml_str = xml.toprettyxml(indent="   ")

            t = datetime.datetime.now()
            date_str = t.strftime('%Y_%m_%d')

            filename = wsdl['WSDL_GLOB_PATH'].replace('*', date_str)
            with open(filename, "w") as f:
                f.write(xml_str)

    def build_action_list(self):
        # Sort the list of actions by the action name
        sorted_actions = sorted(self.all_actions, key=itemgetter('name'))
        action_data = self.jinja_render_file(ACTION_INFORMATION_PATH,
                                            {'all_actions': sorted_actions})
        first_line = action_data.split('\n')[0]
        last_line = action_data.split('\n')[-1]
        original_string = None
        with open(README_PATH) as f:
            original_string = f.read()

        first_line_index = original_string.find(first_line)
        last_line_index = original_string.find(last_line)
        if first_line_index and last_line_index:
            last_line_index += len(last_line)

            string_to_replace = original_string[first_line_index:last_line_index]
            new_string = original_string.replace(string_to_replace, action_data)

            with open(README_PATH, "w") as f:
                f.write(new_string)

    def camel_case_to_snake_case(self, name):
        s0 = name.replace('-', '')
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s0)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def jinja_render_file(self, filename, context):
        path, filename = os.path.split(filename)
        return jinja2.Environment(
            loader=jinja2.FileSystemLoader(path or './')
        ).get_template(filename).render(context)

    def jinja_render_str(self, jinja_template_str, context):
        return jinja2.Environment().from_string(jinja_template_str).render(context)

    def render_action(self, context):
        action_data = self.jinja_render_file(ACTION_TEMPLATE_PATH, context)
        action_filename = "{}/{}.yaml".format(ACTION_DIRECTORY,
                                              context['operation_snake_case'])

        self.all_actions.append({'name': "algosec.{0}".format(context['operation_snake_case']),
                                'description': context['operation_description']})

        with open(action_filename, "w") as f:
            f.write(action_data)

    def build_type_dict(self, type_elem):
        elem_type = type_elem.type
        if not elem_type.name:
            return None

        # pylint: disable=no-member
        if isinstance(elem_type, zeep.xsd.types.builtins.BuiltinType):
            if type_elem.accepts_multiple:
                return [elem_type._default_qname.localname]
            else:
                return elem_type._default_qname.localname
        else:
            type_dict = {}
            for attribute_name, attribute_elem in elem_type.elements:
                attribute_obj = self.build_type_dict(attribute_elem)
                type_dict[attribute_name] = attribute_obj

            if type_elem.accepts_multiple:
                type_dict = [type_dict]
        return type_dict

    def get_type_description(self, type_elem):
        type_dict = self.build_type_dict(type_elem)
        # type_desc = pprint.pformat(type_dict)
        type_json = json.dumps(type_dict, indent=2)
        type_json = type_json.replace('\n', '\n       ')
        return (">\n"
                "      'type: {0}\n"
                "       json_schema: {1}'").format(type_elem.type.name,
                                                   type_json)

    def generate_operation(self, operation):
        op_name = operation.name
        op_inputs = []
        op_entry_point = "lib/run_operation.py"

        if op_name == "authenticate":
            op_entry_point = "lib/run_login.py"
        elif op_name == "connect":
            op_entry_point = "lib/run_login.py"

        # Translate operation "inputs" in the SOAP WSDL into StackStorm action
        # parameters
        for input_name, input_elem in operation.input.body.type.elements:
            input_type_obj = input_elem.type
            parameter_required = 'true' if input_elem.min_occurs > 0 else 'false'
            parameter_name = self.camel_case_to_snake_case(input_name)
            parameter_description = None
            parameter_type = None
            parameter_default = None
            if op_name == 'authenticate' and parameter_name == 'username':
                # Utilize our existing 'username' parameter on the action template
                continue
            elif op_name == 'authenticate' and parameter_name == 'password':
                # Utilize our existing 'password' parameter on the action template
                continue
            elif op_name == 'authenticate' and parameter_name == 'domain':
                # Utilize our existing 'password' parameter on the action template
                continue
            elif op_name == 'connect' and parameter_name == 'password':
                # Utilize our existing 'password' parameter on the action template
                continue
            elif op_name == 'connect' and parameter_name == 'user_name':
                # Utilize our existing 'username' parameter on the action template
                continue
            elif op_name == 'connect' and parameter_name == 'domain':
                # Utilize our existing 'username' parameter on the action template
                continue
            elif op_name == 'create_user' and parameter_name == 'password':
                # This is a new password for creating a new user.
                parameter_name = 'user_password'
                parameter_required = True
                parameter_description = ('"Password for the new user"')
            elif op_name == 'update_user' and parameter_name == 'password':
                # This is a new password for creating a new user.
                parameter_name = 'user_password'
                parameter_required = True
                parameter_description = ('"New password to update the user"')
            elif parameter_name == "session_id":
                # The session input is present on every operation.
                # We want to make this optional, and if unspecified we simply
                # perform a login immediately prior to executing the operation.
                parameter_required = False
                parameter_description = ('"Login session cookie. If empty then'
                                         ' username/password will be used to login'
                                         ' prior to running this operation"')
            elif parameter_name == "ffws_header":
                # Adding a default value to ffws_header information
                parameter_default = '{"version":"1.0", "opaque":""}'

            # Ensure that this parameter doesn't conflict with any of the ones
            # we have defined in the aciton template
            if parameter_name in self.action_template_params:
                print("ERROR: Param conflicts with default: {}.{}"
                      .format(op_name, parameter_name))

            # pylint: disable=no-member
            if isinstance(input_type_obj, zeep.xsd.types.builtins.BuiltinType):
                parameter_type = input_type_obj._default_qname.localname
                if parameter_type == "unsignedInt" or parameter_type == "int":
                    parameter_type = "integer"
                elif parameter_type == "date":
                    parameter_type = "string"
            else:
                parameter_description = self.get_type_description(input_elem)
                parameter_type = 'object'

            op_inputs.append({'name': input_name,
                              'parameter_name': parameter_name,
                              'parameter_type': parameter_type,
                              'parameter_description': parameter_description,
                              'parameter_required': parameter_required,
                              'parameter_default': parameter_default})

        # end for each input
        op_description = ("Invokes the AlgoSec SOAP command {0}"
                          .format(op_name))
        op_context = {'operation_camel_case': op_name,
                      'operation_snake_case': "{0}_{1}".format(self.wsdl['NAME'],
                        self.camel_case_to_snake_case(op_name)),
                      'operation_description': op_description,
                      'operation_entry_point': op_entry_point,
                      'operation_parameters': op_inputs,
                      'operation_wsdl_endpoint': self.wsdl['WSDL_ENDPOINT']}
        self.render_action(op_context)

    def generate(self):
        self.all_actions = []
        for wsdl in API_ENDPOINTS:
            self.wsdl = wsdl
            wsdl_path = None
            if self.cli_args.wsdl_path:
                wsdl_path = self.cli_args.wsdl_path
            else:
                wsdl_files = glob.glob(wsdl['WSDL_GLOB_PATH'])
                # find newest wsdl (by name)
                wsdl_path = max(wsdl_files)

            client = zeep.Client(wsdl=wsdl_path)

            # Parse Operations from the WSDL file
            service = client.wsdl.services.values()[0]
            port = service.ports.values()[0]

            for operation in port.binding._operations.values():
                self.generate_operation(operation)

        self.build_action_list()

    def run(self):
        if self.cli_args.command == "fetch-wsdl":
            self.fetch_wsdl()
        elif self.cli_args.command == "generate":
            self.generate()
        else:
            raise RuntimeError("Unknown command {}".format(self.cli_args.command))


if __name__ == "__main__":
    cli = Cli()
    args = cli.parse()
    generator = ActionGenerator(args)
    generator.run()
