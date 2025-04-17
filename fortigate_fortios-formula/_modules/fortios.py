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

def get_version():
    fg = __proxy__['fortios.conn']()

    return fg.get_version()
