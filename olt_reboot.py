#!/usr/bin/python

import mymod
import argparse
import sys

user = 'admin'
passwd = 'XXX'
hostname = '192.168.1.1'


def check_arg(args=None):
    parser = argparse.ArgumentParser(description='Cisco OLT rebooter')
    maingroup = parser.add_argument_group(title='optional')
    maingroup.add_argument('-c', '--check',
                            help='check mode', 
                            action='store_true')
    exgroup = parser.add_argument_group(title='one or the other')
    group = exgroup.add_mutually_exclusive_group(required=True)
    group.add_argument('-s','--slot',
                        help='slot number',
                        default=None)
    group.add_argument('-r','--reboot',
                        help='reboot machine', 
                        action='store_true')

    
    results = parser.parse_args(args)

    return (results.check,
            results.slot,
            results.reboot)


def main():
    
    check, slot, reboot = check_arg(sys.argv[1:])


    ssh = mymod.connect(hostname, user, passwd)
    remote_conn = ssh.invoke_shell()
    print "Interactive SSH session established to %s\n" % hostname
    mymod.send_command(remote_conn)
    
    if check:
        send_confirm = "no"
    else: 
        send_confirm = "yes"

    if reboot:

        send_reboot = "equipment/system/reboot"
        output = mymod.send_command(remote_conn, send_reboot)
        mymod.send_command(remote_conn, send_confirm)
    else:
        send_reboot = "equipment/boards/reboot --slot=" + slot
        output = mymod.send_command(remote_conn, send_reboot)
        mymod.send_command(remote_conn, send_confirm)
       
    remote_conn.close()

if __name__ == "__main__":
    main()

