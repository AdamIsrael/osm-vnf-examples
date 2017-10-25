from charmhelpers.core.hookenv import (
    action_get,
    action_fail,
    action_set,
    config,
    status_set,
)

from charms.reactive import (
    remove_state as remove_flag,
    set_state as set_flag,
    when,
    when_not,
)


@when('actions.hostname')
def hostname():
    err = ''
    try:
        cmd = "hostname"
        result, err = charms.sshproxy._run(cmd)
    except:
        action_fail('command failed:' + err)
    else:
        action_set({'outout': result})
    finally:
        remove_flag('actions.set-server')

@when_not('workshop-demo.installed')
def install_workshop_demo():
   set_state('workshop-demo.installed')
