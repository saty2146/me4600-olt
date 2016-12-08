#!/usr/bin/python

import paramiko
import StringIO
import sys, getopt
import time
import argparse
import socket

dominant = { 
        "pon" : "pon.7",
        "profileID" : 4,
        "pppoeID" : 7,
        "mgmtID" : 1,
        "igmpID" : 5,
        "mcastID" : 6,
        "mgmtUP": 1,
        "igmpUP": 1,
        "pppoeUP": 6,
        "startOnuID" : 10
    }

conf = dominant

def check_arg(args=None):

    parser = argparse.ArgumentParser(description='Cisco OLT manipulator')
    maingroup = parser.add_argument_group(title='required')
    maingroup.add_argument('-H', '--host', 
                        help='host ip', 
                        default='192.168.35.50')
    maingroup.add_argument('-u', '--user',
                        help='user name',
                        default='admin')
    maingroup.add_argument('-p', '--passwd',
                        help='password of the OLT',
                        required='True')
    exgroup = parser.add_argument_group(title='one or the other')
    
    group = exgroup.add_mutually_exclusive_group(required=True)
    group.add_argument('-i','--file',
                        type=argparse.FileType('rt'),
                        help='file os ONU serial numbers')
    group.add_argument('-s','--serialnumber',
                        help='ONU serial number',
                        default=None)

    results = parser.parse_args(args)

    return (results.host,
            results.user,
            results.passwd,
            results.file,
            results.serialnumber)

def send_command(remote_conn, cmd):
    cmd = cmd.rstrip()
    remote_conn.send(cmd + '\n')
    time.sleep(1)
    return remote_conn.recv(1000)

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
        

def main():

    host, user, passwd, filename, serialnumber = check_arg(sys.argv[1:])

    print host
    print user
    print passwd
    print filename
    print serialnumber

    ssh = connect(host, user, passwd)
    # Use invoke_shell to establish an 'interactive session'
    remote_conn = ssh.invoke_shell()
    print "Interactive SSH session established to %s\n" % host
    output = send_command(remote_conn,"\n")
    print output

    
    onuid = conf['startOnuID']

    if serialnumber == None:

        for line in filename:
            line = line.rstrip('\n')
            create_onu = "remote-eq/discovery/create --serial-number=" + line + " --port=" + str(conf['pon']) + " --onuID=" + str(onuid) + " --admin=enable --profileID=" + str(conf['profileID']) + " --register-type=serial-number"
            add_mgmt = "remote-eq/onu/services/add --serviceID=" + str(conf['mgmtID']) + " --port=" + str(conf['pon']) + " --onuID=" + str(onuid) + " --add-onu-port=veip.1 --encryption=disable --upstream-dba-profile-id=" + str(conf['mgmtUP']) + " --admin=enable --ip-mgmt=enable --name=ip-mgmt"
            add_pppoe = "remote-eq/onu/services/add --serviceID=" + str(conf['pppoeID']) + " --port=" + str(conf['pon']) + " --onuID=" + str(onuid) + " --add-onu-port=veip.1 --encryption=disable --upstream-dba-profile-id=" + str(conf['pppoeUP']) + " --admin=enable --name=internet-pppoe"
            add_igmp = "remote-eq/onu/services/add  --serviceID=" + str(conf['igmpID']) + " --port=" + str(conf['pon']) + " --onuID=" + str(onuid) + " --add-onu-port=veip.1 --encryption=disable --upstream-dba-profile-id=" +str(conf['igmpUP']) + " --admin=enable --name=iptv-igmp"
            add_mcast = "remote-eq/onu/services/add --serviceID=" + str(conf['mcastID']) + " --port=" + str(conf['pon']) + " --onuID=" + str(onuid) + " --add-onu-port=veip.1 --admin=enable --name=iptv-multicast"        
            
            
            print "Sending cmd:\n" + create_onu 
            output = send_command(remote_conn, create_onu)
            print output 
            print "\nSending cmd:\n" +  add_mgmt
            output = send_command(remote_conn, add_mgmt)
            print output 
            print "\nSending cmd:\n" +  add_pppoe
            output = send_command(remote_conn, add_pppoe)
            print  output 
            print "\nSending cmd:\n" +  add_igmp
            output = send_command(remote_conn, add_igmp)
            print  output 
            print "\nSending cmd:\n" +  add_mcast
            output = send_command(remote_conn, add_mcast)
            print output 
            onuid += 1
    else:
        line = serialnumber.rstrip('\n')
        create_onu = "remote-eq/discovery/create --serial-number=" + line + " --port=" + str(conf['pon']) + " --onuID=" + str(onuid) + " --admin=enable --profileID=" + str(conf['profileID']) + " --register-type=serial-number"
        add_mgmt = "remote-eq/onu/services/add --serviceID=" + str(conf['mgmtID']) + " --port=" + str(conf['pon']) + " --onuID=" + str(onuid) + " --add-onu-port=veip.1 --encryption=disable --upstream-dba-profile-id=" + str(conf['mgmtUP']) + " --admin=enable --ip-mgmt=enable --name=ip-mgmt"
        add_pppoe = "remote-eq/onu/services/add --serviceID=" + str(conf['pppoeID']) + " --port=" + str(conf['pon']) + " --onuID=" + str(onuid) + " --add-onu-port=veip.1 --encryption=disable --upstream-dba-profile-id=" + str(conf['pppoeUP']) + " --admin=enable --name=internet-pppoe"
        add_igmp = "remote-eq/onu/services/add  --serviceID=" + str(conf['igmpID']) + " --port=" + str(conf['pon']) + " --onuID=" + str(onuid) + " --add-onu-port=veip.1 --encryption=disable --upstream-dba-profile-id=" +str(conf['igmpUP']) + " --admin=enable --name=iptv-igmp"
        add_mcast = "remote-eq/onu/services/add --serviceID=" + str(conf['mcastID']) + " --port=" + str(conf['pon']) + " --onuID=" + str(onuid) + " --add-onu-port=veip.1 --admin=enable --name=iptv-multicast"        
        
        
        print "Sending cmd:\n" + create_onu 
        output = send_command(remote_conn, create_onu)
        print output 
        print "\nSending cmd:\n" +  add_mgmt
        output = send_command(remote_conn, add_mgmt)
        print output 
        print "\nSending cmd:\n" +  add_pppoe
        output = send_command(remote_conn, add_pppoe)
        print  output 
        print "\nSending cmd:\n" +  add_igmp
        output = send_command(remote_conn, add_igmp)
        print  output 
        print "\nSending cmd:\n" +  add_mcast
        output = send_command(remote_conn, add_mcast)
        print output 

       
    remote_conn.close()

if __name__ == "__main__":
    main()

