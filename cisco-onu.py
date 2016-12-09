#!/usr/bin/python

import paramiko
import StringIO
import sys, getopt
import time
import argparse
import socket

dominant = { 
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
        'startOnuID': 15
    }

jegeho = { 
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
        'startOnuID': 47
    }
def check_arg(args=None):

    parser = argparse.ArgumentParser(description='Cisco OLT manipulator')
    maingroup = parser.add_argument_group(title='required')
    maingroup.add_argument('-H', '--host', 
                        help='OLT IP address', 
                        default='192.168.35.50')
    maingroup.add_argument('-u', '--user',
                        help='OLT username',
                        default='admin')
    maingroup.add_argument('-p', '--passwd',
                        help='OLT password',
                        required='True')
    maingroup.add_argument('-o', '--objectprofile', 
                        choices=['dominant','jegeho'],
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

    return (results.host,
            results.user,
            results.passwd,
            results.objectprofile,
            results.file,
            results.serialnumber)

def send_command(remote_conn, cmd):
    
    print "Sending cmd:\n" + cmd + "\n"
    cmd = cmd.rstrip()
    remote_conn.send(cmd + '\n')
    time.sleep(1)
    output = remote_conn.recv(1000)
    print output
    return True

def connect(host, user, passwd):
    
    try:
        # Create instance of SSHClient object
        remote_conn_pre = paramiko.SSHClient()

        # Automatically add untrusted hosts 
        remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # initiate SSH connection
        remote_conn_pre.connect(host, username=user, password=passwd, timeout=5, look_for_keys=False, allow_agent=False)
        print "SSH connection established to %s\n" % host
       
        return remote_conn_pre
    
    except paramiko.AuthenticationException:
        print "Authentication failed when connecting to %s" % host
        sys.exit(1)
    
    except socket.timeout:
        sys.exit("Connection timeout")
        

def create_commands(line,conf,onuid):

    sn = line
    onuid = str(onuid)
    slot = conf['slot']
    pon = conf['pon']
    profileID = conf['profileID']
    pppoeID = conf['pppoeID']
    mgmtID = conf['mgmtID']
    igmpID = conf['igmpID']
    mcastID = conf['mcastID']
    mgmtUP = conf['mgmtUP']
    igmpUP = conf['igmpUP']
    pppoeUP = conf['pppoeUP']


    create_onu = "remote-eq/discovery/create --serial-number=" + sn + " --port=" + pon + " --slot=" + slot + " --onuID=" + onuid + " --admin=enable --profileID=" + profileID + " --register-type=serial-number"
    add_mgmt = "remote-eq/onu/services/add --serviceID=" + mgmtID + " --port=" + pon + " --slot=" + slot + " --onuID=" + onuid + " --add-onu-port=veip.1 --encryption=disable --upstream-dba-profile-id=" + mgmtUP + " --admin=enable --ip-mgmt=enable --name=ip-mgmt --serviceID-onu=1"
    add_pppoe = "remote-eq/onu/services/add --serviceID=" + pppoeID + " --port=" + pon + " --slot=" + slot + " --onuID=" + onuid + " --add-onu-port=veip.1 --encryption=disable --upstream-dba-profile-id=" + pppoeUP + " --admin=enable --name=internet-pppoe --serviceID-onu=2"
    add_igmp = "remote-eq/onu/services/add  --serviceID=" + igmpID + " --port=" + pon +  " --slot=" + slot + " --onuID=" + onuid + " --add-onu-port=veip.1 --encryption=disable --upstream-dba-profile-id=" + igmpUP + " --admin=enable --name=iptv-igmp --serviceID-onu=3"
    add_mcast = "remote-eq/onu/services/add --serviceID=" + mcastID + " --port=" + pon + " --slot=" + slot + " --onuID=" + onuid + " --add-onu-port=veip.1 --admin=enable --name=iptv-multicast --serviceID-onu=4"       
    add_mcast_pkg = "remote-eq/onu/services/mcast-package/create --onuID=" + onuid + " --port=" + pon + " --slot=" + slot + " --serviceID-onu=3 --pkg-id=1"
    
    return (create_onu,
            add_mgmt,
            add_pppoe,
            add_igmp,
            add_mcast,
            add_mcast_pkg) 

def main():

    host, user, passwd, objectprofile, filename, serialnumber = check_arg(sys.argv[1:])
    
    if objectprofile == 'dominant':
        conf = dominant
    elif objectprofile == 'jegeho':
        conf = jegeho
    else:
        print "Error"

    ssh = connect(host, user, passwd)
    # Use invoke_shell to establish an 'interactive session'
    remote_conn = ssh.invoke_shell()
    print "Interactive SSH session established to %s\n" % host
    send_command(remote_conn,"\n")

    
    onuid = conf['startOnuID']

    if serialnumber == None:

        for line in filename:
            line = line.rstrip('\n')
            create_onu, add_mgmt, add_pppoe, add_igmp, add_mcast, add_mcast_pkg = create_commands(line, conf, onuid)
            
            send_command(remote_conn, create_onu)
            send_command(remote_conn, add_mgmt)
            send_command(remote_conn, add_pppoe)
            send_command(remote_conn, add_igmp)
            send_command(remote_conn, add_mcast)
            send_command(remote_conn, add_mcast_pkg)
            onuid += 1
    else:
        line = serialnumber.rstrip('\n')
        create_onu, add_mgmt, add_pppoe, add_igmp, add_mcast, add_mcast_pkg = create_commands(line, conf, onuid)
        
        
        send_command(remote_conn, create_onu)
        send_command(remote_conn, add_mgmt)
        send_command(remote_conn, add_pppoe)
        send_command(remote_conn, add_igmp)
        send_command(remote_conn, add_mcast)
        send_command(remote_conn, add_mcast_pkg)
       
    remote_conn.close()

if __name__ == "__main__":
    main()

