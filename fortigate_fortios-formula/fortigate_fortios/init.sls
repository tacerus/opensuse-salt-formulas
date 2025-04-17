configure_my_fortigate:
  fortios.address_managed:
    - data:
        - name: wildcard_suse_com
          type: fqdn
          fqdn: '*.suse.com'
          allow-routing: disable
