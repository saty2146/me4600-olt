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

user = 'admin'
passwd = 'XXX'
hostname = '192.168.35.51'

def check_arg(args=None):
    parser = argparse.ArgumentParser(description='Cisco ONU removal')
    maingroup = parser.add_argument_group(title='required')
    maingroup.add_argument('-s','--slot',
                        help='slot number',
                        default='1')
    maingroup.add_argument('-o','--pon',
                        help='pon port', 
                        required='True')
    maingroup.add_argument('-n','--sn',
                        help='ONU serial number', 
                        required='True')

    results = parser.parse_args(args)

    return (results.slot,
            results.pon,
            results.sn)


def main():

    slot, pon, onu_sn = check_arg(sys.argv[1:])

    ssh = mymod.connect(hostname, user, passwd)
    remote_conn = ssh.invoke_shell()
    mymod.send_command(remote_conn)

    onu_id, profile_id = mymod.find_onu_id(remote_conn, onu_sn, slot, pon)
    cl_srv = mymod.find_onu_services(remote_conn, slot, pon, onu_id)
    # ("Deleting services ...")
    for srv_id in reversed(sorted(cl_srv.keys())):
        print srv_id
        mymod.remove_onu_service(remote_conn, slot, pon, onu_id, srv_id)
    # ("Removing ONU ...")
    mymod.remove_onu(remote_conn, slot, pon, onu_id)

    remote_conn.close()

if __name__ == "__main__":
    main()
