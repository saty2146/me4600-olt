#!/usr/bin/python
"""
Script for ONUs bulk migration from one SLOT/PON to another SLOT/PON on the same
OLT device.
"""

import mymod
import paramiko
import StringIO
import sys, getopt
import time
import argparse
import socket
import re
from myobject import *

#define OLT 
host = '192.168.35.51'
user = 'admin'
passwd = 'XXX'

#define original SLOT/PON port
from_slot_port = { 'slot': '1', 'pon': 'pon.7' }

#define target SLOT/PON port
to_slot_port = { 'slot': '1', 'pon': 'pon.8' }

def main():

    ssh = mymod.connect(host, user, passwd)
    remote_conn = ssh.invoke_shell()
    mymod.send_command(remote_conn)

    sns = mymod.find_onu_sn(remote_conn, slot, pon)
    for onu_sn in sns:
        onu_id, profile_id = mymod.find_onu_id(remote_conn, onu_sn, pon)
        cl_srv = mymod.find_onu_services(remote_conn, slot, pon, onu_id)
        #print "SN: " + onu_sn
        #print "onu id: " + onu_id
        #print "profileid: " + profile_id
        #print cl_srv
        # ("Deleting services ...")
        for srv_id in reversed(sorted(cl_srv.keys())):
            #print srv_id
            mymod.remove_onu_service(remote_conn, slot, pon, onu_id, srv_id)
        # ("Removing ONU ...")
        mymod.remove_onu(remote_conn, slot, pon, onu_id)
        # ("Finding new free ONU id")
        new_conf = {'slot': new_slot, 'pon': new_pon}
        new_onu_id = mymod.find_next_onu(remote_conn, new_conf)
        #print "Creating ONU ..."
        mymod.add_onu(remote_conn, new_slot, new_pon, onu_sn, new_onu_id, profile_id)
        #print "Creating services ..."
        for srv_id in sorted(cl_srv.keys()):
            service_id = cl_srv[srv_id]['net_srv']
            up_profile = cl_srv[srv_id]['up_profile']
            service_name = cl_srv[srv_id]['srv_name']
            ip_mgmt = cl_srv[srv_id]['ip_mgmt']
            uni_ctag = cl_srv[srv_id]['uni_ctag']

            mymod.add_service(remote_conn, new_slot, new_pon, onu_sn, new_onu_id, service_id, up_profile, service_name, ip_mgmt, uni_ctag)
        
    remote_conn.close()


if __name__ == "__main__":
    main()
