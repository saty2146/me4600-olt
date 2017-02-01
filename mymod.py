#!/usr/bin/python

import paramiko
import StringIO
import sys, getopt
import time
import argparse
import socket
import re

def send_command(remote_conn, cmd=''):
    if not cmd:
	print "Sending cmd: Enter\n"
    else:
    	print "Sending cmd: " + cmd + "\n"
    cmd = cmd.rstrip()
    remote_conn.send(cmd + '\n')
    time.sleep(1)
    output = remote_conn.recv(9000)
    
    buf=StringIO.StringIO(output)

    line = buf.read().split("\n")
    
    row = line[-2].split('|')

    is_error = next((s for s in row if ('Error' in s or 'ERR' in s)), None)    
    
    if is_error:
	print ', '.join(row)
	sys.exit()
    else:
    	print "OK"
    	return output

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
        

def find_last_onu(remote_conn, conf):
    
    slot = conf['slot']
    pon = conf['pon']
    lastonu = 01

    cmd = "remote-eq/onu/show --slot=" + slot + " --port=" + pon
    output = send_command(remote_conn, cmd)
    
    buf=StringIO.StringIO(output)

    line = buf.read().split("\n")
    match = re.search(r'PON', line[-3])
    
    if match:
        raw = re.findall(r'\d+', line[-3])
        onu = raw[2:]
        onu.sort(key=int)
        if len(onu) == 0:
            lastonu = 1
        else:
            lastonu = onu[-1]
    else: 
        onu = re.findall(r'\d+', line[-3])
        onu.sort(key=int)
        print len(onu)
        if len(onu) == 0:
            lastonu = 1
        else:
            lastonu = onu[-1]

    return lastonu



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


    create_onu = "remote-eq/discovery/create --serial-number=" + sn + " --port=" + pon + " --slot=" + slot + " --onuID=" + onuid + " --admin=enable --profileID=" + profileID + " --register-type=serial-number --sw-upgrade-mode=auto"
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

if __name__ == "__main__":
    main()

