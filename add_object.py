#!/usr/bin/python

import mymod
import paramiko
from creds import *

#BASIC SERVICES
parameters = {
    'mgmt': { 'name': 'cisco-onu-mng-vl343',
              'uni-ctag': '343',
              'uni-stag': '343',
              'uplink-lags': '1',
              'downlink-ports': '1.1',
#              'uplink-ports': '1.5',
              'type': 'macbridge',
              'igmp': 'disable',
              'mc-flood': 'disable',
              'mc-proxy': 'disable'
              },
    'igmp': { 'name': 'slnecnice-iptv-igmp',
              'uni-ctag': '40',
              'uni-stag': '988',
              'uplink-lags': '1',
              'downlink-ports': '1.1',
#              'uplink-ports': '1.5',
              'type': 'unicast',
              'igmp': 'enable',
              'mc-flood': 'disable',
              'mc-proxy': 'disable'
              },
    'mcast': {'name': 'iptv-multicast',
              'uni-ctag': '99',
              'uni-stag': '99',
              'uplink-lags': '1',
              'downlink-ports': '1.1',
#              'uplink-ports': '1.5',
              'type': 'multicast',
              'igmp': 'disable',
              'mc-flood': 'disable',
              'mc-proxy': 'enable'
              },
    'pppoe': { 'name': 'slnecnice-pppoe',
               'uni-ctag': '20',
               'uni-stag': '977',
               'uplink-lags': '1',
               'downlink-ports': '1.1',
#              'uplink-ports': '1.5',
               'type': 'macbridge',
               'igmp': 'disable',
               'mc-flood': 'enable',
              'mc-proxy': 'disable'
    }
}

olt = olt_kancel

def create_service(srv):

    service = "/services/create --serviceName=" + srv['name'] + " --uni-ctag=" + srv['uni-ctag'] + " --nni-stag=" + srv['uni-stag'] + " --type=" + srv['type'] + " --stacked=disable --mc-flood=" + srv['mc-flood'] + " --dhcp-v4=disable --dhcp-v6=disable" + " --pppoe=disable" +" --igmp=" + srv['igmp'] + " --dai=disable --mc-proxy=" + srv['mc-proxy'] +  " --add-uplink-lags=" + srv['uplink-lags'] + " --add-downlink-ports=" + srv['downlink-ports'] + " --admin=enable" 
    

#    service = "/services/create --serviceName=" + srv['name'] + " --uni-ctag=" + srv['uni-ctag'] + " --nni-stag=" + srv['uni-stag'] + " --type=" + srv['type'] + " --stacked=disable --mc-flood=" + srv['mc-flood'] + " --dhcp-v4=disable --dhcp-v6=disable" + " --pppoe=disable" +" --igmp=" + srv['igmp'] + " --dai=disable --mc-proxy=" + srv['mc-proxy'] +  " --add-uplink-ports=" + srv['uplink-ports'] + " --add-downlink-ports=" + srv['downlink-ports'] + " --admin=enable" 

    return service


def main():
    myolt = mymod.Olt(olt)
    ssh = myolt.connect()
    remote_conn = ssh.invoke_shell()
    myolt.send_command(remote_conn)
    for key in parameters.keys():
        add_srv = create_service(parameters[key])
        myolt.send_command(remote_conn, add_srv)
    
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
