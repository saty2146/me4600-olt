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

def main():

    olt, profile, sn = mymod.olt_profile(mymod.check_arg)

    if sn is not None:
        myolt = mymod.Olt(olt, profile)
        ssh = myolt.connect()
        remote_conn = ssh.invoke_shell()
        myolt.send_command(remote_conn)

        onu_id = myolt.find_next_onu(remote_conn)
        
        create_onu, add_mgmt, add_pppoe, add_igmp, add_mcast, add_mcast_pkg = myolt.create_commands(sn, onu_id)
        
        
        myolt.send_command(remote_conn, create_onu)
        myolt.send_command(remote_conn, add_mgmt)
        myolt.send_command(remote_conn, add_pppoe)
        myolt.send_command(remote_conn, add_igmp)
        myolt.send_command(remote_conn, add_mcast)
        myolt.send_command(remote_conn, add_mcast_pkg)
      
        remote_conn.close()
    else:
        print ("!!! No ONU SN specified !!!")

if __name__ == "__main__":
    main()

