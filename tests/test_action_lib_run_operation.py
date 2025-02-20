from algosec_base_action_test_case import AlgoSecActionTestCase

from lib.run_operation import RunOperation
from lib.run_operation import CONFIG_CONNECTION_KEYS
from st2common.runners.base_action import Action

import copy
import mock
import zeep
import logging


class TestActionLibRunOperation(AlgoSecActionTestCase):
    __test__ = True
    action_cls = RunOperation

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, RunOperation)
        self.assertIsInstance(action, Action)

    def test_camel_to_snake(self):
        action = self.get_action_instance({})
        snake = "snake_case_string"
        camel = "snakeCaseString"
        result = action.camel_case_to_snake_case(camel)
        self.assertEqual(result, snake)

    def test_snake_to_camel(self):
        action = self.get_action_instance({})
        snake = "snake_case_string"
        camel = "snakeCaseString"
        result = action.snake_to_camel(snake)
        self.assertEqual(result, camel)

    def test__sanitize_operation_args(self):
        action = self.get_action_instance({})
        action.client = zeep.Client(wsdl="./etc/fireflow_wsdl_2018_06_13.xml")
        test_operation = 'createTicket'
        test_dict = {'ffws_header': {"version": "1.0", "opaque": ""},
                     'session_id': 'test',
                     'ticket': "test"}

        expected_dict = {'FFWSHeader': {"version": "1.0", "opaque": ""},
                         'sessionId': 'test',
                         'ticket': "test"}
        result = action._sanitize_operation_args(test_operation, test_dict)
        self.assertEqual(result, expected_dict)

    def test_get_del_arg_present(self):
        action = self.get_action_instance({})
        test_dict = {"key1": "value1",
                     "key2": "value2"}
        test_key = "key1"
        expected_dict = {"key2": "value2"}
        expected_value = test_dict["key1"]
        result_value = action.get_del_arg(test_key, test_dict)
        self.assertEqual(result_value, expected_value)
        self.assertEqual(test_dict, expected_dict)

    def test_get_del_arg_missing(self):
        action = self.get_action_instance({})
        test_dict = {"key1": "value1",
                     "key2": "value2"}
        test_key = "key3"
        expected_dict = test_dict
        expected_value = None
        result_value = action.get_del_arg(test_key, test_dict)
        self.assertEqual(result_value, expected_value)
        self.assertEqual(test_dict, expected_dict)

    def test_resolve_connection_from_config(self):
        action = self.get_action_instance(self.config_good)
        connection_name = 'full'
        connection_config = self.config_good['algosec'][connection_name]
        connection_expected = {'connection': connection_name}
        connection_expected.update(connection_config)
        kwargs_dict = {'connection': connection_name}
        connection_result = action.resolve_connection(kwargs_dict)
        self.assertEqual(connection_result, connection_expected)

    def test_resolve_connection_from_config_missing(self):
        action = self.get_action_instance(self.config_good)
        connection_name = 'this_connection_doesnt_exist'
        kwargs_dict = {'connection': connection_name}
        with self.assertRaises(KeyError):
            action.resolve_connection(kwargs_dict)

    def test_resolve_connection_from_config_defaults(self):
        action = self.get_action_instance(self.config_good)
        connection_name = 'base'
        connection_config = self.config_good['algosec'][connection_name]
        connection_expected = {'connection': connection_name}
        connection_expected.update(connection_config)
        for key, required, default in CONFIG_CONNECTION_KEYS:
            if not required and default:
                connection_expected[key] = default

        kwargs_dict = {'connection': connection_name}
        connection_result = action.resolve_connection(kwargs_dict)
        self.assertEqual(connection_result, connection_expected)

    def test_resolve_connection_from_kwargs(self):
        action = self.get_action_instance(self.config_blank)
        kwargs_dict = {'connection': None,
                       'server': 'kwargs_server',
                       'username': 'kwargs_username',
                       'password': 'kwargs_password',
                       'port': 123,
                       'transport': 'abc123',
                       'wsdl_endpoint': 'xxx?wsdl'}
        connection_expected = copy.deepcopy(kwargs_dict)
        connection_result = action.resolve_connection(kwargs_dict)
        self.assertEqual(connection_result, connection_expected)
        self.assertEqual(kwargs_dict, {})

    def test_resolve_connection_from_kwargs_defaults(self):
        action = self.get_action_instance(self.config_blank)
        kwargs_dict = {'connection': None,
                       'server': 'kwargs_server',
                       'username': 'kwargs_username',
                       'password': 'kwargs_password'}
        connection_expected = copy.deepcopy(kwargs_dict)
        for key, required, default in CONFIG_CONNECTION_KEYS:
            if not required and default:
                connection_expected[key] = default

        connection_result = action.resolve_connection(kwargs_dict)
        self.assertEqual(connection_result, connection_expected)
        self.assertEqual(kwargs_dict, {})

    def test_resolve_connection_from_kwargs_extras(self):
        action = self.get_action_instance(self.config_blank)
        connection_expected = {'connection': None,
                               'server': 'kwargs_server',
                               'username': 'kwargs_username',
                               'password': 'kwargs_password',
                               'port': 123,
                               'transport': 'abc123',
                               'wsdl_endpoint': 'xxx?wsdl'}
        kwargs_dict = copy.deepcopy(connection_expected)
        kwargs_extras = {"extra_key1": "extra_value1",
                         "extra_key2": 234}
        kwargs_dict.update(kwargs_extras)
        connection_result = action.resolve_connection(kwargs_dict)
        self.assertEqual(connection_result, connection_expected)
        self.assertEqual(kwargs_dict, kwargs_extras)

    def test_validate_connection(self):
        action = self.get_action_instance(self.config_blank)
        connection = {}
        for key, required, default in CONFIG_CONNECTION_KEYS:
            if required:
                connection[key] = "value_for_key_{}".format(key)

        result = action.validate_connection(connection)
        self.assertTrue(result)

    def test_validate_connection_missing_raises(self):
        action = self.get_action_instance(self.config_blank)
        connection = {}
        with self.assertRaises(KeyError):
            action.validate_connection(connection)

    def test_validate_connection_none_raises(self):
        action = self.get_action_instance(self.config_blank)
        connection = {}
        for key, required, default in CONFIG_CONNECTION_KEYS:
            connection[key] = None

        with self.assertRaises(KeyError):
            action.validate_connection(connection)

    def test_build_wsdl_url(self):
        action = self.get_action_instance({})
        connection = {'transport': 'https',
                      'server': 'algosec.domain.tld',
                      'wsdl_endpoint': 'WebServices/FireFlow.wsdl'}
        expected_url = ("{0}://{1}/{2}".
                        format(connection['transport'],
                               connection['server'],
                               connection['wsdl_endpoint']))
        wsdl_url = action.build_wsdl_url(connection)
        self.assertEqual(wsdl_url, expected_url)

    def test_build_wsdl_url_port(self):
        action = self.get_action_instance({})
        connection = {'transport': 'https',
                      'server': 'algosec.domain.tld',
                      'port': 8443,
                      'wsdl_endpoint': 'WebServices/FireFlow.wsdl'}
        expected_url = ("{0}://{1}:{2}/{3}".
                        format(connection['transport'],
                               connection['server'],
                               connection['port'],
                               connection['wsdl_endpoint']))
        wsdl_url = action.build_wsdl_url(connection)
        self.assertEqual(wsdl_url, expected_url)

    def test_build_wsdl_url_missing_server(self):
        action = self.get_action_instance({})
        connection = {'transport': 'https',
                      'port': 8443,
                      'wsdl_endpoint': 'WebServices/FireFlow.wsdl'}
        with self.assertRaises(RuntimeError):
            action.build_wsdl_url(connection)

    def test_login(self):
        action = self.get_action_instance(self.config_good)
        kwargs_dict = {'session': None,
                       'operation': "authenticate",
                       'ffws_header': {"version": "1.0", "opaque": ""}}
        connection_name = 'full'
        connection = self.config_good['algosec'][connection_name]
        context = {'connection': connection,
                   'kwargs_dict': kwargs_dict}

        expected_session = "expected_session"

        mock_client = mock.MagicMock()
        mock_operation = mock.Mock()
        mock_operation.return_value = expected_session
        mock_client.service.__getitem__.return_value = mock_operation

        result = action.login(mock_client.service, context)

        mock_operation.assert_called_with(
            FFWSHeader=context['kwargs_dict']['ffws_header'],
            username=context['connection']['username'],
            password=context['connection']['password'],
            domain=None)

        self.assertEqual(result, expected_session)

    @mock.patch('lib.run_operation.zeep.Client')
    def test__pre_exec_kwargs(self, mock_client):
        action = self.get_action_instance(self.config_blank)
        kwargs_dict = {'operation': 'createTicket',
                       'session_id': 'abc123',
                       'server': 'algosec.domain.tld',
                       'username': 'user',
                       'password': 'pass',
                       'ffws_header': {"version": "1.0", "opaque": ""},
                       'wsdl_endpoint': 'WebServices/FireFlow.wsdl'}
        kwargs_dict_extras = {'arg1': 'value1',
                              'arg2': 'value2',
                              'ffws_header': {"version": "1.0", "opaque": ""}}
        kwargs_dict.update(kwargs_dict_extras)
        wsdl_url = ("http://{0}/WebServices/FireFlow.wsdl"
                    .format(kwargs_dict['server']))
        mock_service = mock.Mock(service='mock client')
        mock_client.return_value = mock_service
        expected_context = {'kwargs_dict': kwargs_dict_extras,
                            'operation': kwargs_dict['operation'],
                            'session_id': kwargs_dict['session_id'],
                            'connection': {'connection': None,
                                           'server': kwargs_dict['server'],
                                           'username': kwargs_dict['username'],
                                           'password': kwargs_dict['password'],
                                           'transport': 'http',
                                           'wsdl_endpoint': 'WebServices/FireFlow.wsdl'},
                            'wsdl_url': wsdl_url}
        kwargs_dict_copy = copy.deepcopy(kwargs_dict)

        result_context, result_client = action._pre_exec(**kwargs_dict_copy)
        mock_client.assert_called_with(wsdl=wsdl_url)
        self.assertEqual(result_client, mock_client.return_value.service)
        self.assertEqual(result_context, expected_context)

    @mock.patch('lib.run_operation.zeep.Client')
    def test__pre_exec_config(self, mock_client):
        action = self.get_action_instance(self.config_good)
        connection_name = 'full'
        kwargs_dict = {'operation': 'createTicket',
                       'session_id': None,
                       'ffws_header': {"version": "1.0", "opaque": ""},
                       'connection': connection_name}
        connection = self.config_good['algosec'][connection_name]
        kwargs_dict.update(connection)
        connection['connection'] = connection_name
        kwargs_dict_extras = {'arg1': 'value1',
                              'arg2': 'value2',
                              'ffws_header': {"version": "1.0", "opaque": ""}}
        kwargs_dict.update(kwargs_dict_extras)
        wsdl_url = ("{0}://{1}:{2}/WebServices/FireFlow.wsdl"
                    .format(kwargs_dict['transport'],
                            kwargs_dict['server'],
                            kwargs_dict['port']))
        mock_service = mock.Mock(service='mock client')
        mock_client.return_value = mock_service
        expected_context = {'kwargs_dict': kwargs_dict_extras,
                            'operation': kwargs_dict['operation'],
                            'session_id': kwargs_dict['session_id'],
                            'connection': connection,
                            'wsdl_url': wsdl_url}
        kwargs_dict_copy = copy.deepcopy(kwargs_dict)

        result_context, result_client = action._pre_exec(**kwargs_dict_copy)
        mock_client.assert_called_with(wsdl=wsdl_url)
        self.assertEqual(result_client, mock_client.return_value.service)
        self.assertEqual(result_context, expected_context)

    @mock.patch('lib.run_operation.RunOperation._sanitize_operation_args')
    def test__exec_session(self, mock__sanitize_operation_args):
        action = self.get_action_instance(self.config_blank)
        expected_result = "abc"
        expected_session = "abc123"
        expected_args = {'paramOneValue': 'value1',
                         'paramTwoValue': 'value2',
                         'sessionId': expected_session}
        context = {'kwargs_dict': {'param_one_value': 'value1',
                                   'param_two_value': 'value2',
                                   'ffws_header': {"version": "1.0", "opaque": ""}},
                   'operation': 'createTicket',
                   'session_id': expected_session,
                   'connection': {'server': 'algosec.domain.tld',
                                  'username': 'user',
                                  'password': 'pass',
                                  'wsdl_endpoint': 'WebServices/FireFlow.wsdl'}}

        mock__sanitize_operation_args.return_value = expected_args
        mock_operation = mock.Mock()
        mock_operation.return_value = expected_result
        mock_client = mock.MagicMock()
        mock_client.service.__getitem__.return_value = False
        mock_client.service.__getitem__.return_value = mock_operation

        result = action._exec(context, mock_client.service)

        self.assertFalse(mock_client.service.Login.called)
        mock_client.service.__getitem__.assert_called_with(context['operation'])
        mock_operation.assert_called_with(**expected_args)
        self.assertEqual(result, expected_result)

    @mock.patch('lib.run_operation.RunOperation._sanitize_operation_args')
    def test__exec_login(self, mock__sanitize_operation_args):
        action = self.get_action_instance(self.config_blank)
        expected_result = "abc"
        expected_session = "abc123"
        expected_args = {'paramOneValue': 'value1',
                         'paramTwoValue': 'value2',
                         'sessionId': expected_session}
        context = {'kwargs_dict': {'param_one_value': 'value1',
                                   'param_two_value': 'value2',
                                   'ffws_header': {"version": "1.0", "opaque": ""}},
                   'operation': 'createTicket',
                   'session_id': None,
                   'connection': {'server': 'algosec.domain.tld',
                                  'username': 'user',
                                  'password': 'pass',
                                  'wsdl_endpoint': 'WebServices/FireFlow.wsdl'}}

        mock__sanitize_operation_args.return_value = expected_args
        mock_operation = mock.Mock()
        mock_operation.return_value = expected_result
        mock_login_operation = mock.Mock()
        mock_login_operation.return_value = expected_session
        mock_client = mock.MagicMock()
        mock_client.service.__getitem__.side_effect = [mock_login_operation, mock_operation]

        result = action._exec(context, mock_client.service)

        mock_login_operation.assert_called_with(
            FFWSHeader=context['kwargs_dict']['ffws_header'],
            username=context['connection']['username'],
            password=context['connection']['password'],
            domain=None)
        mock_client.service.__getitem__.assert_called_with(context['operation'])
        mock_operation.assert_called_with(**expected_args)
        self.assertEqual(result, expected_result)

    def test__exec_login_bad_connection(self):
        action = self.get_action_instance(self.config_blank)
        context = {'kwargs_dict': {'param_one_value': 'value1',
                                   'param_two_value': 'value2',
                                   'ffws_header': {"version": "1.0", "opaque": ""}},
                   'operation': 'createTicket',
                   'session_id': None,
                   'connection': {'server': 'algosec.domain.tld',
                                  'wsdl_endpoint': 'WebServices/FireFlow.wsdl'}}
        mock_client = mock.Mock()
        with self.assertRaises(KeyError):
            action._exec(context, mock_client)

    def test__post_exec(self):
        logging.disable(logging.CRITICAL)
        action = self.get_action_instance(self.config_blank)
        client = zeep.Client(wsdl="./etc/fireflow_wsdl_2018_06_13.xml")
        expected = {"customFieldData": {"name": "abc123",
                                        "displayName": "new_field",
                                        "type": None,
                                        "maxValues": None,
                                        "category": None,
                                        "defaultValue": None,
                                        "validation": None}}
        type_class = client.get_type('ns0:customFieldData')
        obj = type_class(name=expected['customFieldData']['name'],
                         displayName=expected['customFieldData']['displayName'])
        result = action._post_exec(obj)
        self.assertEqual(result, expected['customFieldData'])

    @mock.patch("lib.run_operation.RunOperation._post_exec")
    @mock.patch("lib.run_operation.RunOperation._exec")
    @mock.patch("lib.run_operation.RunOperation._pre_exec")
    def test_run(self, mock__pre_exec, mock__exec, mock__post_exec):
        action = self.get_action_instance(self.config_blank)
        kwargs_dict = {'username': 'user',
                       'password': 'pass'}
        context = "context"
        client = "client"
        exec_result = "exec result"
        post_exec_result = "post exec result"

        mock__pre_exec.return_value = (context, client)
        mock__exec.return_value = exec_result
        mock__post_exec.return_value = post_exec_result

        result = action.run(**kwargs_dict)

        mock__pre_exec.assert_called_with(**kwargs_dict)
        mock__exec.assert_called_with(context, client)
        mock__post_exec.assert_called_with(exec_result)
        self.assertEqual(result, post_exec_result)
