#!/usr/bin/python

import mymod
import paramiko
import StringIO
import sys, getopt
import time
import argparse
import socket
import re
from myobject import *

def check_arg(args=None):

    parser = argparse.ArgumentParser(description='Cisco OLT manipulator')
    maingroup = parser.add_argument_group(title='required')
    maingroup.add_argument('-u', '--user',
                        help='OLT username',
                        default='admin')
    maingroup.add_argument('-p', '--passwd',
                        help='OLT password',
                        required='True')
    maingroup.add_argument('-o', '--objectprofile', 
                        choices=['dominant','jegeho_dole','jegeho_hore','slnecnice_3etapa_B1_B2','slnecnice_3etapa_B3_B4','primyte_1etapa_1vl','shc3_olt_pon7','shc3_olt_pon8'],
                        help='OLT object profile',
                        required='True')
    exgroup = parser.add_argument_group(title='one or the other')
    
    group = exgroup.add_mutually_exclusive_group(required=True)
    group.add_argument('-i','--file',
                        type=argparse.FileType('rt'),
                        help='file name of ONU serial numbers')
    group.add_argument('-s','--serialnumber',
                        help='ONU serial number',
                        default=None)

    results = parser.parse_args(args)

    return (results.user,
            results.passwd,
            results.objectprofile,
            results.file,
            results.serialnumber)


def main():

    user, passwd, objectprofile, filename, serialnumber = check_arg(sys.argv[1:])
    
    if objectprofile == 'dominant':
        conf = dominant
    elif objectprofile == 'jegeho_dole':
        conf = jegeho_dole
    elif objectprofile == 'jegeho_hore':
        conf = jegeho_hore
    elif objectprofile == 'slnecnice_3etapa_B1_B2':
        conf = slnecnice_3etapa_B1_B2
    elif objectprofile == 'slnecnice_3etapa_B3_B4':
        conf = slnecnice_3etapa_B3_B4
    elif objectprofile == 'primyte_1etapa_1vl':
        conf = primyte_1etapa_1vl
    elif objectprofile == 'shc3_olt_pon7':
        conf = shc3_olt_pon7
    elif objectprofile == 'shc3_olt_pon8':
        conf = shc3_olt_pon8
    else:
        print "No Object profile specified"

    host = conf['host']
    ssh = mymod.connect(host, user, passwd)
    # Use invoke_shell to establish an 'interactive session'
    remote_conn = ssh.invoke_shell()
    mymod.send_command(remote_conn)
    
    onuid = mymod.find_next_onu(remote_conn, conf)

    if serialnumber == None:

        for line in filename:
            line = line.rstrip('\n')
            create_onu, add_mgmt, add_pppoe, add_igmp, add_mcast, add_mcast_pkg = mymod.create_commands(line, conf, onuid)
            
            mymod.send_command(remote_conn, create_onu)
            mymod.send_command(remote_conn, add_mgmt)
            mymod.send_command(remote_conn, add_pppoe)
            mymod.send_command(remote_conn, add_igmp)
            mymod.send_command(remote_conn, add_mcast)
            mymod.send_command(remote_conn, add_mcast_pkg)
            onuid += 1
    else:
        line = serialnumber.rstrip('\n')
        create_onu, add_mgmt, add_pppoe, add_igmp, add_mcast, add_mcast_pkg = mymod.create_commands(line, conf, onuid)
        
        
        mymod.send_command(remote_conn, create_onu)
        mymod.send_command(remote_conn, add_mgmt)
        mymod.send_command(remote_conn, add_pppoe)
        mymod.send_command(remote_conn, add_igmp)
        mymod.send_command(remote_conn, add_mcast)
        mymod.send_command(remote_conn, add_mcast_pkg)
      
    remote_conn.close()

if __name__ == "__main__":
    main()

