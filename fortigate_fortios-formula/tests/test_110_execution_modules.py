"""
Test suite for Salt execution modules in the FortiGate FortiOS formula
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

from lib import salt
import pytest

_family_suffixes = ['', '6']

def test_fortios_get_version(host, device):
    rout, rerr, rc = salt(host, device, 'fortios.get_version')
    assert not rerr

    assert rout[0] == 'v'

def test_fortios_get_license(host, device):
    rout, rerr, rc = salt(host, device, 'fortios.get_license')
    assert not rerr

    # assert a license entry which is assumed to always exist
    assert 'vdom' in rout
    assert 'can_upgrade' in rout['vdom']

@pytest.mark.parametrize('fs', _family_suffixes)
def test_fortios_get_address(host, device, fs):
    rout, rerr, rc = salt(host, device, f'fortios.get_address{fs}')
    assert not rerr

    assert isinstance(rout, list)

    entry = next(iter(rout))

    assert 'name' in entry
    assert 'q_origin_key' in entry

@pytest.mark.parametrize('fs', _family_suffixes)
def test_fortios_get_address(host, device, fs):
    rout, rerr, rc = salt(host, device, f'fortios.get_addrgrp{fs}')
    assert not rerr

    assert isinstance(rout, list)

    if fs == '':
        entry = next(iter(rout))
        assert 'name' in entry
        assert 'member' in entry
    elif fs == '6':
        # empty by default
        assert not rout

@pytest.mark.parametrize('service', ['', 'FTP'])
def test_fortios_get_service(host, device, service):
    rout, rerr, rc = salt(host, device, f'fortios.get_service {service}')
    assert not rerr

    if service == '':
        assert isinstance(rout, list)
        assert len(rout) > 1
        entry = next(iter(rout))
    else:
        assert isinstance(rout, dict)
        entry = rout

    assert 'name' in entry
    assert 'q_origin_key' in entry

@pytest.mark.parametrize('group', ['', 'Email Access'])
def test_fortios_get_service_group(host, device, group):
    if group != '':
        group = f'"{group}"'

    rout, rerr, rc = salt(host, device, f'fortios.get_service_group {group}')
    assert not rerr

    if group == '':
        assert isinstance(rout, list)
        assert len(rout) > 1
        entry = next(iter(rout))
    else:
        assert isinstance(rout, dict)
        entry = rout

    assert 'name' in entry
    assert 'q_origin_key' in entry
    assert 'member' in entry

@pytest.mark.parametrize('fs', _family_suffixes)
@pytest.mark.parametrize('route', ['', '1'])
def test_fortios_get_static_route(host, device, fs, route):
    rout, rerr, rc = salt(host, device, f'fortios.get_static_route{fs} {route}')
    assert not rerr

    if route == '':
        assert isinstance(rout, list)

        # no static v6 routes by default
        if fs == '':
            assert len(rout) > 0
            entry = next(iter(rout))
    else:
        assert isinstance(rout, dict)
        entry = rout

    if fs == '':
        assert 'q_origin_key' in entry
        assert 'seq-num' in entry

    else:
        assert not rout


@pytest.mark.parametrize('fs', _family_suffixes)
@pytest.mark.parametrize('ippool', ['', '1'])
def test_fortios_get_ippool(host, device, fs, ippool):
    rout, rerr, rc = salt(host, device, f'fortios.get_ippool{fs} {ippool}')
    assert not rerr

    if ippool == '':
        assert isinstance(rout, list)
    else:
        assert isinstance(rout, dict)

    # no ippools by default
    assert not rout

@pytest.mark.parametrize('policy', ['', '1'])
def test_fortios_get_policy(host, device, policy):
    rout, rerr, rc = salt(host, device, f'fortios.get_policy {policy}')
    assert not rerr

    if policy == '':
        assert isinstance(rout, list)
        assert len(rout) > 0
        entry = next(iter(rout))
    else:
        assert isinstance(rout, dict)
        entry = rout

    assert 'q_origin_key' in entry
    assert entry.get('policyid') == 1

@pytest.mark.parametrize('interface', ['', 'internal3'])
def test_fortios_get_interface(host, device, interface):
    rout, rerr, rc = salt(host, device, f'fortios.get_interface {interface}')
    assert not rerr

    if interface == '':
        assert isinstance(rout, list)
        assert len(rout) > 1
        entry = next(iter(rout))
    else:
        assert isinstance(rout, dict)
        entry = rout
        assert entry.get('name') == 'internal3'

    assert 'status' in entry
    assert 'stp' in entry

@pytest.mark.parametrize('zone', ['', 'foo'])
def test_fortios_get_zone(host, device, zone):
    rout, rerr, rc = salt(host, device, f'fortios.get_zone {zone}')
    assert not rerr

    if zone == '':
        assert isinstance(rout, list)
    else:
        assert isinstance(rout, dict)

    # no zones by default
    assert not rout
