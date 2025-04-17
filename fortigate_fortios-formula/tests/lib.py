"""
Helper functions for testing the FortiGate FortiOS formula
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

from fabric import Config, Connection
import json

def fg_ssh(target):
    return Connection(target, config=Config(user_ssh_path='ssh_config'))

def fg_exec(connection, command):
    res = connection.run(command)
    if res.exited != 0:
        raise RuntimeError
    return res.stdout

def salt(host, device, command):
    #print(command)
    result = host.run(f'/usr/bin/salt --out json {device} {command}')
    try:
        return json.loads(result.stdout)[device], result.stderr, result.rc
    except:
        raise RuntimeError('General Salt failure')

def salt_state_single(host, device, state, name, state_kwargs='', test=False):
    return salt(host, device, f'state.single fortios.{state} name={name} {state_kwargs} test={test}')

def salt_state_single_data(host, device, state, name, data, test=False):
    data = json.dumps(data)
    return salt_state_single(host, device, state, name, f'data=\'{data}\'', test)

def salt_state_apply(host, device, state, test=False):
    return salt(host, device, f'state.apply fortios.{state} test={test}')
