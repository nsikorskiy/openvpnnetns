#!/usr/bin/env python3.10

import os
import sys
import subprocess
import ipaddress

script_type = os.getenv('script_type')
script_context = os.getenv('script_context')
netns_name = os.getenv('openvpn_netns_name')


def up():
    """Up tun iface"""
    tun_name = os.getenv('dev')
    tun_ip = os.getenv('ifconfig_local')
    tun_mask = os.getenv('ifconfig_netmask')
    tun_mtu = os.getenv('tun_mtu')

    ip = ipaddress.IPv4Interface(f'{tun_ip}/{tun_mask}')
    broadcast = ip.network.broadcast_address.compressed
    iprout_ip = ip.with_prefixlen


    subprocess.call(['/bin/ip', 'link', 'set', tun_name, 'netns', netns_name])
    subprocess.call(['/bin/ip', '-n', netns_name, 'link', 'set', tun_name, 'mtu', tun_mtu])
    subprocess.call(['/bin/ip', '-n', netns_name, 'link', 'set', tun_name, 'up'])
    subprocess.call(['/bin/ip', '-n', netns_name, 'addr', 'add', iprout_ip, 'broadcast', broadcast, 'dev', tun_name])
    subprocess.call(['/bin/ip', '-n', netns_name, 'addr'])
    print('up ok')

def route_up():
    tun_name = os.getenv('dev')
    route_vpn_gateway = os.getenv('route_vpn_gateway')
    subprocess.call(['/bin/ip', '-n', netns_name, 'route', 'add',  'default', 'via', route_vpn_gateway, 'dev', tun_name])
    subprocess.call(['/bin/ip', '-n', netns_name, 'route'])

    foreign_options = [ os.environ[opt].split() for opt in os.environ.keys() if 'foreign_option' in opt]
    ns_list = [ value for prefix, opt_name, value in foreign_options  if prefix == 'dhcp-option' and opt_name == 'DNS'  ]

    with open(F'/etc/netns/{netns_name}/resolv.conf', 'w') as fd:
        for ns in ns_list:
            fd.write(F'nameserver {ns}\n')

    subprocess.call(['cat', F'/etc/netns/{netns_name}/resolv.conf'])
    print('route up ok')

def route_pre_down():
    print('route down ok')

def down():
    print('down ok')



def main():
    match (script_type, script_context):
        case ('up', 'init'):
            up()
        case ('route-up', 'init'):
            route_up()
        case ('route-pre-down', 'init'):
            route_pre_down()
        case ('down', 'init'):
            down()
        case _:
            print(f"No match script_type: {script_type}, script_context: {script_context}")


if __name__ == '__main__':
    main()
