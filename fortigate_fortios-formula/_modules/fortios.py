"""
Salt execution module with FortiGate FortiOS related utilities
Copyright (C) 2025 SUSE LLC <georg.pfuetzenreuter@suse.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import logging

try:
    from fortiosapi import FortiOSAPI, InvalidLicense, NotLogged

    HAS_FORTIOS = True

except ImportError:
    HAS_FORTIOS = False

log = logging.getLogger(__name__)
__proxyenabled__ = ['fortios']

def __virtual__():
    if HAS_FORTIOS and 'proxy' in __opts__:
        return 'fortios'
    else:
        return (
            False,
            'Missing dependency: the fortios Salt modules require the "fortiosapi" Python module.',
        )

def _result(data, flatten):
    __salt__['log.debug'](f'fortios: {data}')
    if 'results' in data:
        results = data['results']

        if flatten:
            if len(results) > 1:
                __salt__['log.error']('fortios: more than one result for given mkey, results will not be accurate')
            return next(iter(data['results']))

        return data['results']

    elif 'status' in data and data['status'] == 'error':
        if data['http_method'] == 'GET' and data['http_status'] == 404 and flatten:
            return {}

        return False

def get_version():
    fg = __proxy__['fortios.conn']()

    return fg.get_version()

def get_license():
    fg = __proxy__['fortios.conn']()

    return _result(fg.license(), False)

###
# BEGIN get FUNCTIONS
###

def get(path, name, vdom=None, mkey=None, parameters=None):
    fg = __proxy__['fortios.conn']()

    return _result(fg.get(path, name, vdom, mkey, parameters), flatten=bool(mkey))

def get_address(address=None, vdom=None):
    fg = __proxy__['fortios.conn']()

    return get('firewall', 'address', mkey=address, vdom=vdom)

def get_address6(address=None, vdom=None):
    fg = __proxy__['fortios.conn']()

    return get('firewall', 'address6', mkey=address, vdom=vdom)

def get_addrgrp(addrgrp=None, vdom=None):
    fg = __proxy__['fortios.conn']()

    return get('firewall', 'addrgrp', mkey=addrgrp, vdom=vdom)

def get_addrgrp6(addrgrp=None, vdom=None):
    fg = __proxy__['fortios.conn']()

    return get('firewall', 'addrgrp6', mkey=addrgrp, vdom=vdom)

def get_service(service=None, vdom=None):
    fg = __proxy__['fortios.conn']()

    return get('firewall.service', 'custom', mkey=service, vdom=vdom)

def get_service_group(service_group=None, vdom=None):
    fg = __proxy__['fortios.conn']()

    return get('firewall.service', 'group', mkey=service_group, vdom=vdom)

def get_static_route(route=None, vdom=None):
    fg = __proxy__['fortios.conn']()

    return get('router', 'static', mkey=route, vdom=vdom)

def get_static_route6(route=None, vdom=None):
    fg = __proxy__['fortios.conn']()

    return get('router', 'static6', mkey=route, vdom=vdom)

def get_ippool(ippool=None, vdom=None):
    fg = __proxy__['fortios.conn']()

    return get('firewall', 'ippool', mkey=ippool, vdom=vdom)

def get_ippool6(ippool=None, vdom=None):
    fg = __proxy__['fortios.conn']()

    return get('firewall', 'ippool6', mkey=ippool, vdom=vdom)

def get_policy(policy=None, vdom=None):
    fg = __proxy__['fortios.conn']()

    return get('firewall', 'policy', mkey=policy, vdom=vdom)

# in current FortiOS, there is no "policy6", IPv6 policies are part of "policy"

def get_interface(interface=None, vdom=None):
    fg = __proxy__['fortios.conn']()

    return get('system', 'interface', mkey=interface, vdom=vdom)

def get_zone(zone=None, vdom=None):
    fg = __proxy__['fortios.conn']()

    return get('system', 'zone', mkey=zone, vdom=vdom)

###
# END get FUNCTIONS
###

###
# START set FUNCTIONS
###

def set(path, name, data, vdom=None, mkey=None,):
    __salt__['log.debug'](f'fortios set() data: {data}')

    fg = __proxy__['fortios.conn']()

    result = fg.set(path, name, data, mkey, vdom)

    __salt__['log.debug'](f'fortios set() result: {result}')
    __salt__['log.info'](f'fortios set() change revision: {result["revision"]}')

    return result['status'] == 'success'

###
# END set FUNCTIONS
###

