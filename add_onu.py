#!/usr/bin/python

import mymod
import paramiko
import StringIO
import sys, getopt
import time
import argparse
import socket
import re

dominant = {
        'host': '192.168.35.50',
        'slot': '1',
        'pon': 'pon.7',
        'profileID': '4',
        'pppoeID': '7',
        'mgmtID': '1',
        'igmpID': '5',
        'mcastID': '6',
        'mgmtUP':'1',
        'igmpUP':'1',
        'pppoeUP':'6',
    }

jegeho_dole = { 
        'host': '10.4.1.150',
        'slot': '3',
        'pon': 'pon.7',
        'profileID': '3',
        'pppoeID': '2',
        'mgmtID': '5',
        'igmpID': '3',
        'mcastID': '1',
        'mgmtUP':'1',
        'igmpUP':'1',
        'pppoeUP':'4',
    }

jegeho_hore = { 
        'host': '10.4.1.150',
        'slot': '3',
        'pon': 'pon.8',
        'profileID': '3',
        'pppoeID': '2',
        'mgmtID': '5',
        'igmpID': '3',
        'mcastID': '1',
        'mgmtUP':'1',
        'igmpUP':'1',
        'pppoeUP':'4',
    }

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
                        choices=['dominant','jegeho_dole','jegeho_hore'],
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
    else:
        print "No Object profile specified"

    host = conf['host']
    ssh = mymod.connect(host, user, passwd)
    # Use invoke_shell to establish an 'interactive session'
    remote_conn = ssh.invoke_shell()
    print "Interactive SSH session established to %s\n" % host
    mymod.send_command(remote_conn,"\n")
    
    lastonuid = mymod.find_last_onu(remote_conn, conf)
     
    onuid = int(lastonuid) + 1

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

