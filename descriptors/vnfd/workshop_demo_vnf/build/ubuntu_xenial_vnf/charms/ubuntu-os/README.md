# Overview

This charm provides OS-specific functionality for users of Ubuntu. This can be used as a standalone charm, similar to the Ubuntu charm, to get fresh Ubuntu machine, or be included in any charm intended for deployment on Ubuntu to enable these extra features.

Goals:
- Manage Kernel parameters (sysctl)
- ~~Enable unattended upgrades~~
- Enable live kernel upgrades
- Enable landscape
- Expose OS metrics such as uptime and io (disk, network, etc) utilization.
- Support operation by proxy, such as VNF Configuration Charms that manage an application running on a separate host.

# Usage

# Actions

| Action        | Description           | Parameter(s)  |
| ------------- |:-------------:| -----:|
| enable-unattended-upgrades    |Enable unattended upgrades.| components, blacklist |
| disable-unattended-upgrades   |Disable unattended upgrades| None |

## Known Limitations and Issues

# Configuration

# Contact Information

## Upstream Project Name
