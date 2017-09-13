#!/usr/bin/python

import re
import mymod
import paramiko
import argparse
import StringIO
from creds import *
from myobject import *

def check_arg(args=None):
    olts = ['olt_nova_mytna', 'olt_shc3', 'olt_dc4', 'olt_kancel']
    parser = argparse.ArgumentParser(description='OLT PON ADD OBJECT(PROFILE)')
    mand = parser.add_argument_group(title='mandatory arguments')
    mand.add_argument('-o', '--olt', choices = olts, help=', '.join(olts), metavar='', required='True')
    mand.add_argument('-n', '--name', help='name of profile will be used as prefix', metavar='', required='True')
    mand.add_argument('-g', '--gpon_ports', help='gpon ports (format: slot.port: 1.1,1.2)', metavar='', required='True')
    opt = parser.add_argument_group(title='optional arguments')
    opt.add_argument('-m', '--mgmt_vlan', help='mgmt vlan (uni-ctag = uni-stag)', metavar='', nargs="?")
    opt.add_argument('-i', '--igmp_vlan', help='igmp vlan (uni-stag)', metavar='', nargs="?")
    opt.add_argument('-p', '--pppoe_vlan', help='pppoe vlan (uni-stag)', metavar='', nargs="?")
    args = parser.parse_args(args)
    return (args.olt, args.name, args.mgmt_vlan, args.igmp_vlan, args.pppoe_vlan, args.gpon_ports)

def choose_olt(olt_arg):

    macbridge = 'macbridge'
    if olt_arg == 'olt_nova_mytna':
        olt = olt_nova_mytna
    elif olt_arg == 'olt_shc3':
        olt = olt_shc3
    elif olt_arg == 'olt_dc4':
        olt = olt_dc4
        macbridge = 'mac bridge'
    elif olt_arg == 'olt_kancel':
        olt = olt_kancel
    else:
        print ("No OLT specified")
    return (olt, macbridge)

def create_parameters(name, mgmt_vlan, igmp_vlan, pppoe_vlan, gpon_ports, macbridge):
    """
    Create basic network services
    """
    
    parameters = {}

    if mgmt_vlan is not None:
        parameters['mgmt'] = {
                'name': name + '-mng-vlan' + mgmt_vlan,
                'uni-ctag': mgmt_vlan,
                'uni-stag': mgmt_vlan,
                'uplink-lags': '1',
                'downlink-ports': gpon_ports,
#                'uplink-ports': '1.5',
                'type': macbridge,
                'igmp': 'disable',
                'mc-flood': 'disable',
                'mc-proxy': 'disable'
                }
    if igmp_vlan is not None: 
        parameters['igmp'] = {
                'name': name + '-igmp',
                'uni-ctag': '40',
                'uni-stag': igmp_vlan,
                'uplink-lags': '1',
                'downlink-ports': gpon_ports,
#                'uplink-ports': '1.5',
                'type': 'unicast',
                'igmp': 'enable',
                'mc-flood': 'disable',
                'mc-proxy': 'disable'
                }
    if pppoe_vlan is not None:
        parameters['pppoe'] = {
                'name': name + '-pppoe',
                'uni-ctag': '20',
                'uni-stag': pppoe_vlan,
                'uplink-lags': '1',
                'downlink-ports': gpon_ports,
#                'uplink-ports': '1.5',
                'type': macbridge,
                'igmp': 'disable',
                'mc-flood': 'enable',
                'mc-proxy': 'disable'
                }

    return parameters

def find_service_id(output, srv_list):
    srvs = {}
    buf=StringIO.StringIO(output)
    lines = buf.read().split("\n")
    for line in lines:
        for srv in srv_list:
            srv_regex = re.compile('.*({}).*'.format(srv))
            mo_srv = srv_regex.search(line)
            if mo_srv:
                row = mo_srv.group().split('|')
                srvs[srv] = row[1]
                break
    return srvs

def create_service(srv):

# if LAG is defined as UPLINK PORT
    service = "/services/create --serviceName=" + srv['name'] + " --uni-ctag=" + srv['uni-ctag'] + " --nni-stag=" + srv['uni-stag'] + " --type=" + srv['type'] + " --stacked=disable --mc-flood=" + srv['mc-flood'] + " --dhcp-v4=disable --dhcp-v6=disable" + " --pppoe=disable" +" --igmp=" + srv['igmp'] + " --dai=disable --mc-proxy=" + srv['mc-proxy'] +  " --add-uplink-lags=" + srv['uplink-lags'] + " --add-downlink-ports=" + srv['downlink-ports'] + " --admin=enable" 
    
# if ETH is defined as UPLINK PORT
#    service = "/services/create --serviceName=" + srv['name'] + " --uni-ctag=" + srv['uni-ctag'] + " --nni-stag=" + srv['uni-stag'] + " --type=" + srv['type'] + " --stacked=disable --mc-flood=" + srv['mc-flood'] + " --dhcp-v4=disable --dhcp-v6=disable" + " --pppoe=disable" +" --igmp=" + srv['igmp'] + " --dai=disable --mc-proxy=" + srv['mc-proxy'] +  " --add-uplink-ports=" + srv['uplink-ports'] + " --add-downlink-ports=" + srv['downlink-ports'] + " --admin=enable" 

    return service


def main():
    olt_arg, name, mgmt_vlan, igmp_vlan, pppoe_vlan, gpon_ports = check_arg()
    print olt_arg, name, mgmt_vlan, igmp_vlan, pppoe_vlan, gpon_ports
    olt, macbridge = choose_olt(olt_arg)
    myolt = mymod.Olt(olt)
    ssh = myolt.connect()
    remote_conn = ssh.invoke_shell()
    myolt.send_command(remote_conn)
    parameters = create_parameters(name, mgmt_vlan, igmp_vlan, pppoe_vlan, gpon_ports, macbridge)
    print parameters

    srv_list = [parameters[key]['name'] for key in parameters.keys()]

    for key in parameters.keys():
        add_srv = create_service(parameters[key])
        myolt.send_command(remote_conn, add_srv)
    

    output = myolt.send_command(remote_conn,"services/show")
    srv_ids = find_service_id(output, srv_list)

    remote_conn.close()

#IGMP PROXY
#/multicast/igmp/proxy/config --admin=enable --priority=5 --network-version=2 --client-version=2 --robustness=2 --unsolicited-report-interval=1 --max-records-per-report=64
#MCAST CHANNEL
#/multicast/group-list/create --name="default" --serviceID=3 --ip-address=0.0.0.0 --group-mask=0 --admin=enable --static-group=disable --src-ipv4-addr=any --bandwidth=0
#PACKAGE
#/multicast/packages/create --name="package_all"
#/multicast/packages/association/attach --pkg-id=1 --mcast-channel-id=1

if __name__ == "__main__":
    main()
