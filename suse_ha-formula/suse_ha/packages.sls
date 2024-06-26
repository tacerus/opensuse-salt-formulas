{#-
Salt state file for managing SUSE HA related packages
Copyright (C) 2023-2024 SUSE LLC <georg.pfuetzenreuter@suse.com>

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

{%- from 'suse_ha/map.jinja' import fencing -%}

suse_ha_packages:
  pkg.installed:
    - pkgs:
      - conntrack-tools
      - corosync
      - crmsh
      - fence-agents
      - ldirectord
      - pacemaker
      {%- if grains.osfullname != 'openSUSE Tumbleweed' %}
      - python3-python-dateutil
      {%- endif %}
      - resource-agents
      - virt-top
      {%- if 'sbd' in fencing %}
      - sbd
      {%- endif %}
