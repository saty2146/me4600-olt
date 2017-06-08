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
passwd = 'LedaMetis2012'
hostname = '192.168.35.51'

#define custom conf dictionary

#define well known dictionary from myobject or use custom conf
conf = slnecnice_3etapa_B1_B2

#custom conf{}

#conf = { 'slot': '1',
#        'pon': 'pon.6'
#        }
#

def main():
    
    ssh = mymod.connect(hostname, user, passwd)
    remote_conn = ssh.invoke_shell()
    olt = mymod.Olt()
    olt.send_command(remote_conn)
    output = olt.find_next_onu(remote_conn, conf)
    print output

    remote_conn.close()


if __name__ == "__main__":
    main()
