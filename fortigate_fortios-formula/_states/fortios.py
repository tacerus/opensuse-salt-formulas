"""
Salt state module for managing FortiGate FortiOS
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

from json import dumps
import logging

def _list_of_dicts_to_dict(data):
    out = {}

    for item in data:
        name = item.pop('name')

        if name in out:
            raise ValueError('Duplicate')

        out[name] = item

    return out

# possible "data":
#        name,
#        subnet, main_type, route_tag, sub_type, clearpass_spt, macaddr, start_ip, end_ip,
#        fqdn, country, wildcard_fqdn, cache_ttl, wildcard, sdn, fsso_group, interface, tenant,
#        organization, epg_name, subnet_name, sdn_tag, policy_group, obj_tag, obj_type,
#        tag_detection_level, tag_type, hw_vendor, hw_model, os, sw_version, comment,
#        associated_interface, color, match_filter, sdn_addr_type, node_ip_only, obj_id, addr_list,
#        tagging, allow_routing, fabrig_object
# maybe set "type" based on other keys? it will default to "subnet", which is bogus if only "fqdn" is passed

def address_managed(name, data, vdom=None, purge=False):
    ret = {'name': name, 'result': None, 'changes': {}, 'comment': ''}

    if isinstance(data, dict):
        if 'name' in data:
            address = data['name']
        else:
            address = name

        data = [data]

    else:
        address = None

    current = __salt__['fortios.get_address'](address=address, vdom=vdom)

    if isinstance(current, dict):
        current = [current]

    addresses = {
            'have': current,
            'want': data,
            'delete': [],
            'update': {},
            'create': {},
    }

    for state in addresses:
        try:
            addresses[state] = _list_of_dicts_to_dict(addresses[state])

        except ValueError:
            if state == 'have':
                __salt__['log.error'](f'fortios address_managed(): duplicate address on device: {name}')
            elif state == 'want':
                __salt__['log.error'](f'fortios address_managed(): duplicate address in input: {name}')

            ret['result'] = False
            return ret

    if purge:
        for addr in addresses['have']:
            if addr not in addresses['want']:
                __salt__['log.debug'](f'fortios address_managed(): marking address {addr} for deletion')
                addresses['delete'].append(addr)

    for addr, addrdata_want in addresses['want'].items():
        if addr in addresses['have']:
            addrdata_have = addresses['have'][addr]

            if addrdata_want == addrdata_have:
                __salt__['log.debug'](f'fortios address_managed(): nothing to do for address {addr} (full match)')
                continue

            addresses['update'][addr] = {}
            for k, v in addrdata_have.items():
                __salt__['log.debug'](f'fortios address_managed(): reading option {k}')
                if k in addrdata_want:
                    __salt__['log.debug'](f'fortios address_managed(): comparing wanted option {k}')
                    if v != addrdata_want[k]:
                        __salt__['log.debug'](f'fortios address_managed(): marking option {k} for update')
                        addresses['update'][addr].update({k: addrdata_want[k]})
                else:
                    __salt__['log.debug'](f'fortios address_managed(): option {k} does not exist in wanted data, ignoring')

            if not addresses['update'][addr]:
                __salt__['log.debug'](f'fortios address_managed(): no existing options require updates')
                del addresses['update'][addr]

        else:
            addresses['create'][addr] = addrdata_want

    change_addresses = {
            'create': [],
            'delete': addresses['delete'],
            'update': [],
    }

    for x in ['create', 'update']:
        for addr, addrdata in addresses[x].items():
            change_addresses[x].append(
                    {
                        'name': addr,
                        **addrdata,
                    }
            )

    actionmap = {
            'create': 'Created',
            'update': 'Changed',
            'delete': 'Deleted',
    }

    for action, entries in change_addresses.items():
        #comment = '{}Would {} addresses:\n{}\n=====\n'.format(
        #        comment, action,
        #        dumps(change_addresses['create'], indent=4)
        #)

        if entries:
            ret['changes'][action.upper()] = entries

            le = len(entries)
            word = 'address'
            if le > 1:
                word = f'{word}es'

            if __opts__['test']:

                ret['comment'] = '{}Would {} {} {}.\n'.format(
                        ret['comment'], action, le, word
                    )

                continue

        commented = False

        if action == 'delete':
            # TODO
            pass

        elif action in ['create', 'update']:
            for entry in entries:
                __salt__['log.debug'](f'fortios address_managed(): sending {entry}')
                res = __salt__['fortios.set']('firewall', 'address', vdom=vdom, data=entry)

                if res is True and not commented:
                    ret['comment'] = '{}{} {} {}.\n'.format(
                            ret['comment'], actionmap[action], le, word
                        )

                    commented = True

                if res is False:
                    comment = ret['comment'].replace(str(le), str(le - 1))
                    ret['comment'] = f'{comment}Failed to {action} {word}.\n'
                    ret['result'] = False

    if not ret['changes'] and ret['comment'] == '':
        ret['comment'] = 'Nothing to do!'

    if __opts__['test']:
        if ret['changes']:
            ret['result'] = None

        else:
            ret['result'] = True

        return ret

    if ret['result'] is not False:
        ret['result'] = True

    return ret
