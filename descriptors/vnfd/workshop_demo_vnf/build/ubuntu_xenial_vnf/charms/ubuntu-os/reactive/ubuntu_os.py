from charmhelpers.core.hookenv import (
    action_fail,
    action_get,
    action_set,
    config,
)
from charmhelpers.fetch import (
    apt_install,
    apt_purge,
)
from charms.reactive import (
    remove_state,
    set_state,
    when,
    when_not,
)

from charms.templating.jinja2 import render

import os
import subprocess


@when_not('vnf-ubuntu-proxy.installed')
def install_vnf_ubuntu_proxy():
    # Do your setup here.
    #
    # If your charm has other dependencies before it can install,
    # add those as @when() clauses above., or as additional @when()
    # decorated handlers below
    #
    # See the following for information about reactive charms:
    #
    #  * https://jujucharms.com/docs/devel/developer-getting-started
    #  * https://github.com/juju-solutions/layer-basic#overview
    #
    set_state('vnf-ubuntu-proxy.installed')


@when('actions.disable-unattended-upgrades')
def disable_unattended_upgrades():
    """ """

    try:
        packages = ['unattended-upgrades']
        apt_purge(packages)
        os.remove("/etc/apt/apt.conf.d/50unattended-upgrades")
    except subprocess.CalledProcessError as e:
        action_fail('Command failed: %s (%s)' %
                    (' '.join(e.cmd), str(e.output)))
    finally:
        remove_state('actions.disable-unattended-upgrades')


@when('actions.enable-unattended-upgrades')
def enable_unattended_upgrades():
    """Enable unattended upgrades."""

    try:
        packages = ['unattended-upgrades']
        apt_install(packages)

        components = action_get("components").split(',')
        components = list(filter(None, [x.strip(' ') for x in components]))

        blacklist = action_get("blacklist").split(',')
        blacklist = list(filter(None, [x.strip(' ') for x in blacklist]))

        render(
            "etc/apt/apt.conf.d/50unattended-upgrades",
            "/etc/apt/apt.conf.d/50unattended-upgrades", {
                'components': components,
                'blacklist': blacklist,
            }
        )

    except subprocess.CalledProcessError as e:
        action_fail('Command failed: %s (%s)' %
                    (' '.join(e.cmd), str(e.output)))
    finally:
        remove_state('actions.enable-unattended-upgrades')
