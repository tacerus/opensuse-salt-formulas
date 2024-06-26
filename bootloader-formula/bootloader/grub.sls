{#-
Salt state file for managing GRUB configuration
Copyright (C) 2023-2024 Georg Pfuetzenreuter <mail+opensuse@georg-pfuetzenreuter.net>

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

{%- from 'bootloader/map.jinja' import grub_data -%}

{%- if 'config' in grub_data %}
{%- set file = '/etc/default/grub' %}
grub_header:
  file.prepend:
    - name: {{ file }}
    - text: {{ pillar.get('managed_by_salt_formula', '# Managed by the bootloader formula') | yaml_encode }}

{%- set boolmap = {true: 'true', false: 'false'} %}
grub_default:
  file.keyvalue:
    - name: {{ file }}
    - key_values:
      {%- for k, v in grub_data['config'].items() %}
        {%- if v is sameas True or v is sameas False %}
          {%- set value = boolmap[v] %}
        {%- else %}
          {%- set value = v %}
        {%- endif %}
        {{ k | upper }}: '"{{ value }}"'
      {%- endfor %}
    - ignore_if_missing: {{ opts['test'] }}
    - append_if_not_found: True
    - uncomment: '#'

{%- if grub_data.get('update', True) %}
{%- set files = grub_data.get('grub_configuration', '/boot/grub2/grub.cfg') %}
{%- if files is string %}
{%- set files = [files] %}
{%- endif %}
{%- set main = files.pop(0) %}

grub_update:
  cmd.run:
    - name: /usr/sbin/grub2-mkconfig -o {{ main }}
    - onchanges:
      - file: grub_default

{%- if files | length %}

grub_update_copies:
  file.copy:
    - source: {{ main }}
    - names:
     {%- for file in files %}
      - {{ file }}
     {%- endfor %}
    - onchanges:
      - file: grub_default
    - require:
      - cmd: grub_update

{%- endif %} {#- close files check -#}
{%- endif %} {#- close update check -#}
{%- endif %} {#- close config check -#}
