"""
Test suite for Salt state modules in the FortiGate FortiOS formula
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

from lib import salt_state_single_data
import pytest

_data_single = {
        'address': [
            {
                'name': 'wildcard_suse_com',
                'type': 'fqdn',
                'fqdn': '*.suse.com',
                'allow-routing': 'disable',
            }
        ],
}

_data_multi = {
        'address': [
            {
                'name': 'wildcard_opensuse_org',
                'type': 'fqdn',
                'fqdn': '*.opensuse.org',
            },
            {
                'name': 'opensuse_de',
                'type': 'fqdn',
                'fqdn': 'opensuse.de',
            },
        ],
}

_parametrized_testbools = [(True, False), (False, False), (False, True), (True, True)]

def _parametrized_data(subset):
    return [_data_single[subset], _data_multi[subset]]

@pytest.mark.parametrize('test,applied', _parametrized_testbools)
@pytest.mark.parametrize('data', _parametrized_data('address'))
def test_fortios_address_managed(host, device, test, applied, data):
    rout, rerr, rc = salt_state_single_data(host, device, 'address_managed', 'test_address_managed', data, test)
    assert not rerr

    stateout = rout['fortios_|-test_address_managed_|-test_address_managed_|-address_managed']

    datalen = len(data)
    csuffix = 'es' if datalen > 1 else ''

    assert 'comment' in stateout
    if test is True and applied is False:
        assert stateout['comment'] == f'Would create {datalen} address{csuffix}.\n'
        assert stateout['result'] is None

    elif test is False and applied is False:
        assert stateout['comment'] == f'Created {datalen} address{csuffix}.\n'

    else:
        assert stateout['comment'] == 'Nothing to do!'

    assert 'changes' in stateout
    changes = stateout['changes']

    if applied is True:
        assert not changes
        assert stateout['result'] is True

        return

    assert 'CREATE' in changes
    create = changes['CREATE']
    assert isinstance(create, list)
    assert len(create) == datalen
    for i, entry in enumerate(create):
        assert 'name' in entry
        assert entry['name'] == data[i]['name']
        assert entry.get('fqdn') == data[i]['fqdn']
