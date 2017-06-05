#!/usr/bin/python

from __future__ import print_function
import paramiko
import StringIO
import sys, getopt
import time
import argparse
import socket
import re

def send_command(remote_conn, cmd=''):
    if not cmd:
        print ("Sending cmd: Enter", end='')
        paddle = 85
    else:
        paddle = 90 - len(cmd)
    	print ("Sending cmd: " + cmd, end='')
    cmd = cmd.rstrip()
    remote_conn.send(cmd + '\n')
    time.sleep(1)
    output = remote_conn.recv(9000)
    
    buf=StringIO.StringIO(output)

    line = buf.read().split("\n")
    
    row = line[-2].split('|')

    is_error = next((s for s in row if ('Error' in s or 'ERR' in s)), None)    
    
    if is_error:
        print (', '.join(row))
        sys.exit()
    else:
        message = "OK!"
    	print (message.rjust(paddle))
    	return output

def connect(host, user, passwd):
    
    try:
        # Create instance of SSHClient object
        remote_conn_pre = paramiko.SSHClient()

        # Automatically add untrusted hosts 
        remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # initiate SSH connection
        remote_conn_pre.connect(host, username=user, password=passwd, timeout=5, look_for_keys=False, allow_agent=False)
        cmd = "SSH connection established to " + host
        message = "OK!"
        paddle = 103 - len(cmd)
        #print ("SSH connection established to %s" % host, end = '')
        print (cmd, end = '')
    	print (message.rjust(paddle))
       
        return remote_conn_pre
    
    except paramiko.AuthenticationException:
        print ("Authentication failed when connecting to %s" % host)
        sys.exit(1)
    
    except socket.timeout:
        sys.exit("Connection timeout")
        
def find_next_onu(remote_conn, conf):
    
    slot = conf['slot']
    pon = conf['pon']
    nextonu = 0
    onu_id_list = []

    cmd = "remote-eq/discovery/show --slot=" + slot + " --port=" + pon
    output = send_command(remote_conn, cmd)
    
    buf=StringIO.StringIO(output)

    lines = buf.read().split("\n")
    slot_regex = re.compile(r".*({}).*".format('PON'))
    for line in lines[3:]:
        mo_slot = slot_regex.search(line)
        if mo_slot:
            row = mo_slot.group().split('|')
            if row[3].strip() != '--':
                onu_id_list.append(int(row[3]))
            else:
                pass

    if len(onu_id_list) == 0:
        nextonu = 0
    else:
        onu_id_list.sort(key=int)
        nextonu = onu_id_list[-1] + 1

    return nextonu

def find_onu_id(remote_conn, onu_sn, slot, pon):
    
    cmd = "remote-eq/discovery/show --matching-serial-number=" + onu_sn + " --slot=" + slot + " --port=" + pon
    onuid = None
    profileid = None

    output = send_command(remote_conn, cmd)
    
    buf=StringIO.StringIO(output)

    lines = buf.read().split("\n")
    sn_regex = re.compile(".*({}).*".format(onu_sn))
    for line in lines[3:]:
        mo_sn = sn_regex.search(line)
        if mo_sn:
            row = mo_sn.group().split('|')
            onuid = row[3]
            profile = row[8][1]
            profileid = profile[0]
            break
        else:
            pass
    if onuid is None:
        sys.exit('Error!')
        print (onuid)
    else:
        print (onuid)
        return (onuid, profileid)

def find_onu_sn(remote_conn, slot, pon):
    
    sns = []

    cmd = "remote-eq/discovery/show  --slot=" + slot + " --port=" + pon
    output = send_command(remote_conn, cmd)
    
    buf=StringIO.StringIO(output)

    lines = buf.read().split("\n")
    sn_regex = re.compile(r".*({}).*".format('PON'))
    for line in lines[3:]:
        mo_sn = sn_regex.search(line)
        if mo_sn:
            row = mo_sn.group().split('|')
            if row[3].strip() != '--':
                sns.append(row[6])
        else:
            pass

    return sns

def find_onu_services(remote_conn, slot, pon, onuid):
   
    cl_srv = {}
    cl_srv_ids = []
    net_srv_ids = []

    cmd = "remote-eq/onu/services/show --slot=" + slot + " --port=" + pon + " --onuID=" + onuid
    output = send_command(remote_conn, cmd)
    
    buf=StringIO.StringIO(output)

    lines = buf.read().split("\n")
    srv_regex = re.compile(r".*\(\d\).*")
    for line in lines[3:]:
        mo_srv = srv_regex.search(line)
        if mo_srv:
            row = mo_srv.group().split('|')
            cl_srv_id = int(row[1])
            cl_srv.setdefault(cl_srv_id, {})
            cl_srv[cl_srv_id]['net_srv'] = int(row[4][1])
            cl_srv[cl_srv_id]['srv_name'] = row[3]
            cl_srv[cl_srv_id]['uni_ctag'] = int(row[10])
            cl_srv[cl_srv_id]['ip_mgmt'] = 1 if row[11].strip() == 'enable' else 0
            cl_srv[cl_srv_id]['up_profile'] = int(row[5][1]) if row[5][1] != '-' else 0
        else:
            pass

    return cl_srv

def remove_onu_service(remote_conn, slot, pon, onuid, srvid):
   
    cmd = "remote-eq/onu/services/remove --slot=" + slot + " --port=" + pon + " --onuID=" + str(onuid) + " --serviceID-onu=" + str(srvid)
    #print (cmd)
    output = send_command(remote_conn, cmd)
    
def remove_onu(remote_conn, slot, pon, onuid):
   
    cmd = "remote-eq/discovery/remove --slot=" + slot + " --port=" + pon + " --onuID=" + str(onuid)
    #print (cmd)
    output = send_command(remote_conn, cmd)
    
def add_onu(remote_conn, slot, pon, sn, newonuid, profileid):
    newonuid = str(newonuid)
   
    cmd = "remote-eq/discovery/create --serial-number=" + sn + " --port=" + pon + " --slot=" + slot + " --onuID=" + newonuid + " --admin=enable --profileID=" + profileid + " --register-type=serial-number --sw-upgrade-mode=auto"
    #print (cmd)
    output = send_command(remote_conn, cmd)
    
def add_service(remote_conn, slot, pon, sn, newonuid, serviceid, upprofile, service_name, ipmgmt, unictag):
    newonuid = str(newonuid)
    serviceid = str(serviceid)
    
    if ipmgmt:
        upprofile = str(upprofile)
        cmd = "remote-eq/onu/services/add --serviceID=" + serviceid + " --port=" + pon + " --slot=" + slot + " --onuID=" + newonuid + " --add-onu-port=veip.1 --encryption=disable --upstream-dba-profile-id=" + upprofile + " --admin=enable --name=" + service_name +  " --serviceID-onu=" + serviceid + " --ip-mgmt=enable"
    elif upprofile:
        upprofile = str(upprofile)
        cmd = "remote-eq/onu/services/add --serviceID=" + serviceid + " --port=" + pon + " --slot=" + slot + " --onuID=" + newonuid + " --add-onu-port=veip.1 --encryption=disable --upstream-dba-profile-id=" + upprofile + " --admin=enable --name=" + service_name +  " --serviceID-onu=" + serviceid
    else:
        cmd = "remote-eq/onu/services/add --serviceID=" + serviceid + " --port=" + pon + " --slot=" + slot + " --onuID=" + newonuid + " --add-onu-port=veip.1 --admin=enable --name=" + service_name +  " --serviceID-onu=" + serviceid

    output = send_command(remote_conn, cmd)
    
    if unictag == 40:
        cmd = "remote-eq/onu/services/mcast-package/create --onuID=" + newonuid + " --port=" + pon + " --slot=" + slot + " --serviceID-onu=" + serviceid + " --pkg-id=1"
        output = send_command(remote_conn, cmd)
    else:
        pass

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

