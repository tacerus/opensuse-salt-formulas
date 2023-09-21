{#-
Salt state file for managing network interfaces using Wicked
Copyright (C) 2023 Georg Pfuetzenreuter <mail+opensuse@georg-pfuetzenreuter.net>

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
-#}

{%- from 'network/wicked/map.jinja' import base, base_backup, ifcfg_defaults, interfaces, script -%}
{%- set ifcfg_data = {} %}
{%- set startmode_ifcfg = {'auto': [], 'off': []} %}

include:
  - .common

{%- for interface, config in interfaces.items() %}
{%- do ifcfg_data.update({ interface: {'addresses': [], 'startmode': 'auto', 'bootproto': 'static'} }) %}

{%- if 'address' in config %}
{%- set addr = config['address'] %}
{%- elif 'addresses' in config %}
{%- set addr = config['addresses'] %}
{%- else %}
{%- set addr = None %}
{%- endif %}

{%- if addr is string %}
{%- do ifcfg_data[interface]['addresses'].append(addr) %}
{%- elif addr is iterable and addr is not mapping %}
{%- do ifcfg_data[interface]['addresses'].extend(addr) %}
{%- endif %}

{%- for option, value in config.items() %}
{%- if value is sameas true %}
{%- set value = 'yes' %}
{%- elif value is sameas false %}
{%- if option == 'startmode' %}
{%- set value = 'off' %}
{%- else %}
{%- set value = 'no' %}
{%- endif %}
{%- else %}
{%- set value = value | lower %}
{%- endif %}
{%- if not option in ['address', 'addresses'] %}
{%- do ifcfg_data[interface].update({option: value}) %}
{%- endif %}
{%- endfor %}

{%- if ifcfg_data[interface]['startmode'] in startmode_ifcfg.keys() %}
{%- do startmode_ifcfg[ifcfg_data[interface]['startmode']].append(interface) %}
{%- endif %}

{%- endfor %}

{%- if ifcfg_data %}
network_wicked_ifcfg_backup:
  file.copy:
    - names:
      {%- for interface in ifcfg_data.keys() %}
      {%- set file = base ~ '/ifcfg-' ~ interface %}
      {%- if salt['file.file_exists'](file) %}
      - {{ base_backup }}/ifcfg-{{ interface }}:
        - source: {{ file }}
      {%- endif %}
      {%- endfor %}
    - require:
      - file: network_wicked_backup_directory

network_wicked_ifcfg_settings:
  file.managed:
    - names:
      {%- for interface, config in ifcfg_data.items() %}
      - {{ base }}/ifcfg-{{ interface }}:
        - contents:
          {%- for address in config.pop('addresses') %}
            - IPADDR_{{ loop.index }}='{{ address }}'
          {%- endfor %}
          {%- for key, value in config.items() %}
          {%- if value is string %}
            - {{ key | upper }}='{{ value }}'
          {%- else %}
          {%- do salt.log.warning('wicked: unsupported value for key ' ~ key) %}
          {%- endif %}
          {%- endfor %}
      {%- endfor %}
    - mode: '0640'
    - require:
      - file: network_wicked_ifcfg_backup
{%- endif %}

{%- if startmode_ifcfg['auto'] or startmode_ifcfg['off'] %}
network_wicked_interfaces:
  cmd.run:
    - names:
      {%- for interface in startmode_ifcfg['auto'] %}
      - {{ script }}up {{ interface }}:
        - stateful:
          - test_name: {{ script }}up {{ interface }} test
        {%- if salt['cmd.retcode'](cmd='ifstatus ' ~ interface ~ ' -o quiet', ignore_retcode=True) == 0 %}
        - onchanges:
          - file: {{ base }}/ifcfg-{{ interface }}
        {%- endif %}
      {%- endfor %}
      {%- for interface in startmode_ifcfg['off'] %}
      - {{ script }}down {{ interface }}:
        - stateful:
          - test_name: {{ script }}down {{ interface }} test
        - onlyif: ifstatus {{ interface }} -o quiet
      {%- endfor %}
    - require:
      - file: network_wicked_script
      - file: network_wicked_ifcfg_backup
      - file: network_wicked_ifcfg_settings
{%- endif %}
