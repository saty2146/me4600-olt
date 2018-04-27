#!/usr/bin/python

import re
import mymod
import paramiko
import argparse
import StringIO
from creds import *
from myobject import *


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
                print row
                srvs[srv] = row[1]
                break
    return srvs


olt = olts['olt_dc4']

def main():
    myolt = mymod.Olt(olt)
    ssh = myolt.connect()
    remote_conn = ssh.invoke_shell()
    myolt.send_command(remote_conn)


#    srv_list = [parameters['mgmt']['name'], parameters['igmp']['name'], parameters['pppoe']['name']]
    srv_list = ['novy_ruzinov6-mng-vlan325', 'novy_ruzinov7-iptv-igmp', 'novy_ruzinov6-pppoe']

    output = myolt.send_command(remote_conn,"services/show")
    srv_ids = find_service_id(output, srv_list)
    print srv_ids

    remote_conn.close()

if __name__ == "__main__":
    main()
