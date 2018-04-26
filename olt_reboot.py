#!/usr/bin/python

import mymod
import argparse
import sys
from creds import *

OLT = [name for name in olts.keys()]

def check_arg(args=None):

    parser = argparse.ArgumentParser(description='Cisco OLT rebooter')
    mand = parser.add_argument_group(title='mandatory arguments')
    mand.add_argument('-o', '--olt', choices = olts, help=', '.join(OLT), metavar='', required='True')

    exgroup = parser.add_argument_group(title='one or the other')
    group = exgroup.add_mutually_exclusive_group(required=True)
    group.add_argument('-s','--slot', help='slot number', default=None)
    group.add_argument('-r','--reboot', help='reboot machine', action='store_true')
    
    opt = parser.add_argument_group("optional arguments")
    opt.add_argument('-c', '--check', help='check mode', action='store_true')
    
    args = parser.parse_args(args)

    return (args.olt, args.check, args.slot, args.reboot)

def main():
    
    olt_arg, check, slot, reboot = check_arg(sys.argv[1:])

    if olt_arg in OLT:
        olt = olts[olt_arg]
    else:
        print ("No OLT specified")

    myolt = mymod.Olt(olt)
    ssh = myolt.connect()
    remote_conn = ssh.invoke_shell()
    myolt.send_command(remote_conn)

    if check:
        send_confirm = "no"
    else: 
        send_confirm = "yes"

    if reboot:

        send_reboot = "equipment/system/reboot"
        output = myolt.send_command(remote_conn, send_reboot)
        myolt.send_command(remote_conn, send_confirm)
    else:
        send_reboot = "equipment/boards/reboot --slot=" + slot
        output = myolt.send_command(remote_conn, send_reboot)
        myolt.send_command(remote_conn, send_confirm)
       
    remote_conn.close()

if __name__ == "__main__":
    main()
