#!/usr/bin/python
##
# Copyright 2016 Canonical Ltd.
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
##

from testtools import TestCase
import mock


import sys
# import charmhelpers
from charmhelpers.core.hookenv import (
    config,
)
# Nuke the @cache decorator for our tests
# mock.patch('charmhelpers.core.hookenv.cache', lambda x: x).start()

sys.path.append('lib')
import charms.sshproxy


def patch_config(data):
    """Patch the "charmhelpers.core.hookenv.config" function.

    The mocked function returns the given value.
    """
    print("returning mock")
    # return mock.patch(
    #     'charmhelpers.core.hookenv.config',
    #     lambda: data)
    return mock.patch(
        'charmhelpers.core.hookenv.config',
        side_effect=data, autospec=True)


# def mock_config(scope=None):
#     if scope is None:
#         return config
#     return config.get(scope, None)
# mocks.append(patch('charmhelpers.core.hookenv.config',
#                    side_effect=mock_config, autospec=True))


class UnitTests(TestCase):
    """Test."""

    def setUp(self):
        """Setup."""
        super(UnitTests, self).setUp()

    @mock.patch('charms.sshproxy.ssh')
    @mock.patch('subprocess.Popen')
    def test_sshproxy_run(self, mock_popen, mock_ssh):
        """Test."""
        cmd = "echo 0xdeadbeef"

        data = {
            'ssh-hostname': 'foo',
            'ssh-username': 'bar',
            'ssh-password': 'baz',
            'ssh-private-key': 'bad',
        }

        with patch_config(data):
            # cfg = charmhelpers.core.hookenv.config()
            cfg = config()
            print(cfg)
            self.assertEqual(cfg, data)
            charms.sshproxy._run(cmd)

        # process_mock = mock.Mock()
        # attrs = {'communicate.return_value': ('output', 'error')}
        # process_mock.configure_mock(**attrs)
        # mock_popen.return_value = process_mock
        #
        # mock_ssh.return_value = True
        # (out, err) = mock_ssh._run(cmd)


        # charms.sshproxy._run(cmd)


    # @mock.patch('charmhelpers.core.hookenv.config')
    # @mock.patch('subprocess.Popen')
    # @mock.patch('charms.sshproxy._run')
    # def test_ssh_run(self, run, mock_popen, mock_config):
    #     """Test charms.ssh._run()."""
    #     cmd = "echo 0xdeadbeef"
    #
    #     # Mock the config module
    #     config_mock = mock.Mock()
    #     attrs = {
    #         'ssh-hostname': 'foo',
    #         'ssh-username': 'bar',
    #         'ssh-password': 'baz',
    #     }
    #     config_mock.configure_mock(**attrs)
    #     mock_config.return_value = config_mock
    #
    #     process_mock = mock.Mock()
    #     attrs = {'communicate.return_value': ('output', 'error')}
    #     process_mock.configure_mock(**attrs)
    #     mock_popen.return_value = process_mock
    #
    #     charms.sshproxy._run(cmd)
    #     run.assert_called_with(cmd)
    #
    #     self.assertTrue(mock_config.called)
    #     self.assertTrue(mock_popen.called)

        # run.isinstance.assert_called_with(cmd, str)
        # run.ssh.assert_called_with("some command")

    # @mock.patch('actions.run')
    # def test_action_run(self, cmd):
    #     pass
#
#
# if __name__ == '__main__':
#     unittest.main()
