"""
Salt proxy module for FortiGate appliances running FortiOS
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

__proxyenabled__ = ['fortios']
thisproxy = {}

log = logging.getLogger(__file__)

def __virtual__():
    log.debug('fortios __virtual__() ...')

    if not HAS_FORTIOS:
        return (
            False,
            'Missing dependency: the fortios Salt modules require the "fortiosapi" Python module.',
        )

    return 'fortios'

def init(opts):
    log.debug('fortios init() ...')

    fg = FortiOSAPI()
    fg.debug('on')

    try:
        popts = opts['proxy']
        thisproxy['initialized'] = fg.tokenlogin(
                popts['host'],
                popts['token'],
                popts.get('verify', True),
                popts.get('cert', None),
                popts.get('timeout', 10),
                popts.get('vdom', 'root')
        )

    except Exception as ex:
        log.error(f'fortios proxy initialization failed: {ex}')
        thisproxy['initialized'] = False
        return

    thisproxy['conn'] = fg

def conn():
    return thisproxy['conn']

def ping():
    try:
        conn().check_session()
        return True
    except (
            InvalidLicense,
            NotLogged,
    ) as ex:
        log.error(f'fortios ping failed: {ex}')
        return False

def alive(opts):
    if ping():
        return True
    
    log.error('fortios is not alive!')
    return False

def shutdown():
    return conn().logout()

def version():
    return conn().get_version()
