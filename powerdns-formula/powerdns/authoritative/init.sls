{#-
Salt state file for managing the PowerDNS authoritative nameserver
Copyright (C) 2024 Georg Pfuetzenreuter <mail+opensuse@georg-pfuetzenreuter.net>

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

{%- from 'powerdns/map.jinja' import authoritative -%}
{%- set backends = authoritative.get('backends', []) -%}

{%- if authoritative %}

powerdns_authoritative_package:
  pkg.installed:
    - pkgs:
        - pdns
        {%- for backend in backends %}
        - pdns-backend-{{ backend }}
        {%- endfor %}

powerdns_authoritative_config:
  file.managed:
    - name: /etc/pdns/pdns.conf
    - user: root
    - group: pdns
    - mode: '0640'
    - contents:
        - {{ pillar.get('managed_by_salt_formula', '# Managed by the PowerDNS formula') | yaml_encode }}
        {%- for key, value in authoritative.get('config', {}) | dictsort %}
          {%- if value is iterable and value is not string %}
            {%- set value = ','.join(value) %}
          {%- elif value is sameas true %}
            {%- set value = 'yes' %}
          {%- elif value is sameas false %}
            {%- set value = 'no' %}
          {%- endif %}
        - '{{ key }}={{ value }}'
        {%- endfor %}
    - require:
        - pkg: powerdns_authoritative_package

powerdns_authoritative_service:
  service.running:
    - name: pdns
    - enable: true
    - require:
        - pkg: powerdns_authoritative_package
    - watch:
        - file: powerdns_authoritative_config

{%- endif %}

powerdns_authoritative_package_remove:
  pkg.removed:
    - pkgs:
        {%- if not authoritative %}
        - pdns
        {%- endif %}
        {%- for backend in [
                  'godbc',
                  'ldap',
                  'lua',
                  'mysql',
                  'postgresql',
                  'remote',
                  'sqlite',
            ]
        %}
        {%- if backend not in backends %}
        - pdns-backend-{{ backend }}
        {%- endif %}
