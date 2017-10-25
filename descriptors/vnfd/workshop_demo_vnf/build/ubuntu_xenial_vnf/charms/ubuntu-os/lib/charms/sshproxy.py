"""Module to help with executing commands over SSH."""
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

from charmhelpers.core.hookenv import (
    config,
    log,
)
import copy
import io
import json
import paramiko
import os

from subprocess import (
    Popen,
    CalledProcessError,
    PIPE,
)


def charm_dir():
    """Return the root directory of the current charm."""
    d = os.environ.get('JUJU_CHARM_DIR')
    if d is not None:
        return d
    return os.environ.get('CHARM_DIR')


def run_local(cmd, env=None):
    """Run a command locally."""
    if isinstance(cmd, str):
        cmd = cmd.split(' ') if ' ' in cmd else [cmd]

    p = Popen(cmd,
              env=env,
              shell=True,
              stdout=PIPE,
              stderr=PIPE)
    stdout, stderr = p.communicate()
    retcode = p.poll()
    if retcode > 0:
        raise CalledProcessError(returncode=retcode,
                                 cmd=cmd,
                                 output=stderr.decode("utf-8").strip())
    return (stdout.decode('utf-8').strip(), stderr.decode('utf-8').strip())


def _run(cmd, env=None):
    """Run a command, either on the local machine or remotely via SSH."""
    if isinstance(cmd, str):
        cmd = cmd.split(' ') if ' ' in cmd else [cmd]

    cfg = None
    try:
        cfg = config()
    except CalledProcessError as e:
        # We may be running in a restricted context, such as the
        # collect-metrics hook, so attempt to read the persistent config
        # TODO: Make this a patch to charmhelpers.hookenv.config()
        # cfg = Config()
        CONFIG = os.path.join(charm_dir(), '.juju-persistent-config')
        cfg = {}
        with open(CONFIG) as f:
            data = json.load(f)
            log(data)
            for k, v in copy.deepcopy(data).items():
                if k not in cfg:
                    log("{}={}".format(k, v))
                    cfg[k] = v
    finally:
        pass

    if all(k in cfg for k in ['ssh-hostname', 'ssh-username',
                              'ssh-password', 'ssh-private-key']):
        host = cfg['ssh-hostname']
        user = cfg['ssh-username']
        passwd = cfg['ssh-password']
        key = cfg['ssh-private-key']  # DEPRECATED

        if host and user:
            return ssh(cmd, host, user, passwd, key)

    return run_local(cmd, env)


def get_ssh_client(host, user, password=None, key=None):
    """Return a connected Paramiko ssh object."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    pkey = None

    # Check for the DEPRECATED private-key
    if key:
        f = io.StringIO(key)
        pkey = paramiko.RSAKey.from_private_key(f)
    else:
        # Otherwise, check for the auto-generated private key
        if os.path.exists('/root/.ssh/id_juju_sshproxy'):
            with open('/root/.ssh/id_juju_sshproxy', 'r') as f:
                pkey = paramiko.RSAKey.from_private_key(f)

    ###########################################################################
    # There is a bug in some versions of OpenSSH 4.3 (CentOS/RHEL 5) where    #
    # the server may not send the SSH_MSG_USERAUTH_BANNER message except when #
    # responding to an auth_none request. For example, paramiko will attempt  #
    # to use password authentication when a password is set, but the server   #
    # could deny that, instead requesting keyboard-interactive. The hack to   #
    # workaround this is to attempt a reconnect, which will receive the right #
    # banner, and authentication can proceed. See the following for more info #
    # https://github.com/paramiko/paramiko/issues/432                         #
    # https://github.com/paramiko/paramiko/pull/438                           #
    ###########################################################################

    try:
        client.connect(host, port=22, username=user,
                       password=password, pkey=pkey)
    except paramiko.ssh_exception.SSHException as e:
        if 'Error reading SSH protocol banner' == str(e):
            # Once more, with feeling
            client.connect(host, port=22, username=user,
                           password=password, pkey=pkey)
        else:
            # Reraise the original exception
            raise e

    return client


def sftp(local_file, remote_file, host, user, password=None, key=None):
    """Copy a local file to a remote host."""
    client = get_ssh_client(host, user, password, key)

    # Create an sftp connection from the underlying transport
    sftp = paramiko.SFTPClient.from_transport(client.get_transport())
    sftp.put(local_file, remote_file)
    client.close()


def ssh(cmd, host, user, password=None, key=None):
    """Run an arbitrary command over SSH."""
    client = get_ssh_client(host, user, password, key)

    cmds = ' '.join(cmd)
    stdin, stdout, stderr = client.exec_command(cmds, get_pty=True)
    retcode = stdout.channel.recv_exit_status()
    client.close()  # @TODO re-use connections
    if retcode > 0:
        output = stderr.read().strip()
        raise CalledProcessError(returncode=retcode, cmd=cmd,
                                 output=output)
    return (
        stdout.read().decode('utf-8').strip(),
        stderr.read().decode('utf-8').strip()
    )
