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

    olt, profile, sn, loc = mymod.olt_profile(mymod.check_arg)

    if sn is not None and loc is not None:
        myolt = mymod.Olt(olt, profile)
        ssh = myolt.connect()
        remote_conn = ssh.invoke_shell()
        myolt.send_command(remote_conn)

        onu_id = myolt.find_next_onu(remote_conn)
        
        create_onu, add_loc, add_mgmt, add_pppoe, add_igmp, add_mcast, add_mcast_pkg = myolt.create_commands(sn, loc, onu_id)
        
        
        myolt.send_command(remote_conn, create_onu)
        myolt.send_command(remote_conn, add_loc,)
        myolt.send_command(remote_conn, add_mgmt)
        myolt.send_command(remote_conn, add_pppoe)
        myolt.send_command(remote_conn, add_igmp)
        myolt.send_command(remote_conn, add_mcast)
        myolt.send_command(remote_conn, add_mcast_pkg)
      
        remote_conn.close()
    else:
        print ("!!! No ONU SN or LOCATION specified !!!")

if __name__ == "__main__":
    main()

