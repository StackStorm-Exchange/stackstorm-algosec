from algosec_base_action_test_case import AlgoSecActionTestCase

from lib.run_login import RunLogin
from st2common.runners.base_action import Action

import mock


class TestActionLibRunLogin(AlgoSecActionTestCase):
    __test__ = True
    action_cls = RunLogin

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, RunLogin)
        self.assertIsInstance(action, Action)

    @mock.patch("lib.run_operation.RunOperation._pre_exec")
    def test_run_fireflow(self, mock__pre_exec):
        action = self.get_action_instance(self.config_blank)
        connection = {'connection': None,
                      'username': 'user',
                      'password': 'pass',
                      'server': 'aglosec.domain.tld',
                      'wsdl_endpoint': 'WebServices/FireFlow.wsdl'}
        kwargs_dict = {'session': None,
                       'operation': "authenticate",
                       'ffws_header': {"version": "1.0", "opaque": ""}}
        context = {'connection': connection,
                  'kwargs_dict': kwargs_dict}
        expected_session = "xyz123"

        mock_client = mock.MagicMock()
        mock_operation = mock.Mock()
        mock_operation.return_value = expected_session
        mock_client.service.__getitem__.return_value = mock_operation

        mock__pre_exec.return_value = (context, mock_client.service)

        result = action.run(**kwargs_dict)

        mock_operation.assert_called_with(
            FFWSHeader=context['kwargs_dict']['ffws_header'],
            username=context['connection']['username'],
            password=context['connection']['password'],
            domain=None)

        self.assertEqual(result, {'session_id': expected_session})

    @mock.patch("lib.run_operation.RunOperation._pre_exec")
    def test_run_afa(self, mock__pre_exec):
        action = self.get_action_instance(self.config_blank)
        connection = {'connection': None,
                      'username': 'user',
                      'password': 'pass',
                      'server': 'aglosec.domain.tld',
                      'wsdl_endpoint': 'AFA/php/ws.php?wsdl'}
        kwargs_dict = {'session': None,
                       'operation': "connect"}
        context = {'connection': connection,
                  'kwargs_dict': kwargs_dict}
        expected_session = "xyz123"

        mock_client = mock.MagicMock()
        mock_operation = mock.Mock()
        mock_operation.return_value = expected_session
        mock_client.service.__getitem__.return_value = mock_operation

        mock__pre_exec.return_value = (context, mock_client.service)

        result = action.run(**kwargs_dict)

        mock_operation.assert_called_with(
            UserName=context['connection']['username'],
            Password=context['connection']['password'],
            Domain=None)

        self.assertEqual(result, {'session_id': expected_session})
