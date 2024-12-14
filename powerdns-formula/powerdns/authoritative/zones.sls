{#-
Salt state file for managing zones in the PowerDNS authoritative nameserver
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

{%- for zone_name, zone_data in authoritative.get('zones', {}).items() %}

powerdns_authoritative_zone_{{ zone_name }}:
  suse_powerdns.zone_present:
    - name: {{ zone_name }}
    - kind: {{ zone_data['config'].get('kind', 'primary') }}

    # for efficiency upon creation of a new zone, "secure" and "nsec3_params" is passed to zone_present()
    # for existing zones, the settings will be managed by zone_secured()
    - secure: {{ zone_data['config'].get('secure', None) }}
    - nsec3_params: {{ zone_data['config'].get('nsec3', {}) }}

powerdns_authoritative_zone_{{ zone_name }}_dnssec:
  suse_powerdns.zone_secured:
    - name: {{ zone_name }}
    - secure: {{ zone_data['config'].get('secure', None) }}
    - nsec3_params: {{ zone_data['config'].get('nsec3', {}) }}
    - require:
        - suse_powerdns: powerdns_zone_{{ zone_name }}

powerdns_authoritative_zone_{{ zone_name }}_rectify:
  module.run:
    - suse_powerdns.zone_rectify:
        - zone: {{ zone_name }}
    - onchanges:
        - suse_powerdns: powerdns_authoritative_zone_{{ zone_name }}_dnssec
    - require:
        - suse_powerdns: powerdns_zone_{{ zone_name }}

powerdns_authoritative_zone_{{ zone_name }}_serial:
  module.run:
    - suse_powerdns.zone_increase_serial:
        - zone: {{ zone_name }}
    - onchanges:
        - suse_powerdns: powerdns_authoritative_zone_{{ zone_name }}

{%- endfor %}
