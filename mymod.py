#!/usr/bin/python

from __future__ import print_function
import paramiko
import StringIO
import sys, getopt
import time
import argparse
import socket
import re
from myobject import *
from creds import *


def check_arg(args=None):
    """Command line argumnet parser function"""

    olts = ['olt_nova_mytna', 'olt_shc3', 'olt_dc4']
    profiles = ['dominant','jegeho_dole','jegeho_hore','slnecnice_3etapa_B1_B2','slnecnice_3etapa_B3_B4','primyte_1etapa_1vl','shc3_olt_pon7','shc3_olt_pon8','mileticova_60_1vl','mileticova_60_2vl']
    parser = argparse.ArgumentParser(description='OLT PON COMMAND LINE UTILITY')
    mand = parser.add_argument_group(title='mandatory arguments')
    mand.add_argument('-o', '--olt', choices = olts, help=', '.join(olts), metavar='', required='True')
    mand.add_argument('-p', '--profile', choices = profiles, help=', '.join(profiles), metavar='', required='True')
    opt = parser.add_argument_group("mandatory arguments only for add_onu, remove_onu")
    opt.add_argument('-s', '--sn', help='ONU serial number', metavar='', nargs="?")

    args = parser.parse_args(args)

    #print (args.olt, args.profile, args.sn)
    return (args.olt, args.profile, args.sn)

def olt_profile(check_arg):
    """OLT and object profile function"""

    olt_arg, profile_arg, sn_arg = check_arg(sys.argv[1:])
    
    if olt_arg == 'olt_nova_mytna':
        olt = olt_nova_mytna
    elif olt_arg == 'olt_shc3':
        olt = olt_shc3
    elif olt_arg == 'olt_dc4':
        olt = olt_dc4
    else:
        print ("No OLT specified")

    if profile_arg == 'dominant':
        profile = dominant
    elif profile_arg == 'jegeho_dole':
        profile = jegeho_dole
    elif profile_arg == 'jegeho_hore':
        profile = jegeho_hore
    elif profile_arg == 'slnecnice_3etapa_B1_B2':
        profile = slnecnice_3etapa_B1_B2
    elif profile_arg == 'slnecnice_3etapa_B3_B4':
        profile = slnecnice_3etapa_B3_B4
    elif profile_arg == 'primyte_1etapa_1vl':
        profile = primyte_1etapa_1vl
    elif profile_arg == 'shc3_olt_pon7':
        profile = shc3_olt_pon7
    elif profile_arg == 'shc3_olt_pon8':
        profile = shc3_olt_pon8
    elif profile_arg == 'mileticova_60_1vl':
        profile = mileticova_60_1vl
    elif profile_arg == 'mileticova_60_2vl':
        profile = mileticova_60_2vl
    else:
        profile = profile_arg
        print ("No Object profile specified")
    
    return (olt, profile, sn_arg)

class Olt:
 
    """Represents a OLT manipulation class"""

    def __init__(self, olt, profile=None):

        self.host = olt['host']
        self.user = olt['user']
        self.passwd = olt['passwd']
        
        if profile is not None:

            self.slot = profile['slot']
            self.pon = profile['pon']
            self.profileID = profile['profileID']
            self.pppoeID = profile['pppoeID']
            self.mgmtID = profile['mgmtID']
            self.igmpID = profile['igmpID']
            self.mcastID = profile['mcastID']
            self.mgmtUP = profile['mgmtUP']
            self.igmpUP = profile['igmpUP']
            self.pppoeUP = profile['pppoeUP']
            self.mcastPKG = profile['mcastPKG']
        else:
            pass

    def find_bck(self, remote_conn):

        cmd = 'backup-manager/show'
        output = self.send_command(remote_conn, cmd)
        backups = []

        buf=StringIO.StringIO(output)

        lines = buf.read().split("\n")
        file_regex = re.compile(r".*({}).*".format('file'))

        for line in lines:
            mo_bck = file_regex.search(line)
            if mo_bck:
                filename = mo_bck.group().split('|')[1].strip()
                backups.append(filename)
            else:
                pass

        return backups

    def find_next_onu(self, remote_conn):

        self.nextonu = 0
        onu_id_list = []

        cmd = "remote-eq/discovery/show --slot=" + self.slot + " --port=" + self.pon
        output = self.send_command(remote_conn, cmd)

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
            self.nextonu = 0
        else:
            onu_id_list.sort(key=int)
            self.nextonu = onu_id_list[-1] + 1

        return self.nextonu

    def send_command(self, remote_conn, cmd=''):
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

    def connect(self):

        try:
            # Create instance of SSHClient object
            remote_conn_pre = paramiko.SSHClient()

            # Automatically add untrusted hosts
            remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # initiate SSH connection
            remote_conn_pre.connect(self.host, username=self.user, password=self.passwd, timeout=5, look_for_keys=False, allow_agent=False)
            cmd = "SSH connection established to " + self.host
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


    def find_onu_id(self, remote_conn, onu_sn):

        cmd = "remote-eq/discovery/show --matching-serial-number=" + onu_sn + " --slot=" + self.slot + " --port=" + self.pon
        onuid = None
        profileid = None

        output = self.send_command(remote_conn, cmd)

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
            sys.exit('!!!ONU ID not found!!!')
            print (onuid)
        else:
            print (onuid)
            return (onuid, profileid)
    
    def find_onu_services(self, remote_conn, onuid):

        cl_srv = {}
        cl_srv_ids = []
        net_srv_ids = []

        cmd = "remote-eq/onu/services/show --slot=" + self.slot + " --port=" + self.pon + " --onuID=" + onuid
        output = self.send_command(remote_conn, cmd)

        buf=StringIO.StringIO(output)

        lines = buf.read().split("\n")
        srv_regex = re.compile(r".*\(\d+\).*")
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

    def remove_onu_service(self, remote_conn, onuid, srvid):

        cmd = "remote-eq/onu/services/remove --slot=" + self.slot + " --port=" + self.pon + " --onuID=" + str(onuid) + " --serviceID-onu=" + str(srvid)
        #print (cmd)
        output = self.send_command(remote_conn, cmd)

    def remove_onu(self, remote_conn, onuid):

        cmd = "remote-eq/discovery/remove --slot=" + self.slot + " --port=" + self.pon + " --onuID=" + str(onuid)
        #print (cmd)
        output = self.send_command(remote_conn, cmd)

    def create_commands(self, sn, onu_id):

        sn = sn
        onuid = str(onu_id)

        create_onu = "remote-eq/discovery/create --serial-number=" + sn + " --port=" + self.pon + " --slot=" + self.slot + " --onuID=" + onuid + " --admin=enable --profileID=" + self.profileID + " --register-type=serial-number --sw-upgrade-mode=auto"
        add_mgmt = "remote-eq/onu/services/add --serviceID=" + self.mgmtID + " --port=" + self.pon + " --slot=" + self.slot + " --onuID=" + onuid + " --add-onu-port=veip.1 --encryption=disable --upstream-dba-profile-id=" + self.mgmtUP + " --admin=enable --ip-mgmt=enable --name=ip-mgmt --serviceID-onu=1"
        add_pppoe = "remote-eq/onu/services/add --serviceID=" + self.pppoeID + " --port=" + self.pon + " --slot=" + self.slot + " --onuID=" + onuid + " --add-onu-port=veip.1 --encryption=disable --upstream-dba-profile-id=" + self.pppoeUP + " --admin=enable --name=internet-pppoe --serviceID-onu=2"
        add_igmp = "remote-eq/onu/services/add  --serviceID=" + self.igmpID + " --port=" + self.pon +  " --slot=" + self.slot + " --onuID=" + onuid + " --add-onu-port=veip.1 --encryption=disable --upstream-dba-profile-id=" + self.igmpUP + " --admin=enable --name=iptv-igmp --serviceID-onu=3"
        add_mcast = "remote-eq/onu/services/add --serviceID=" + self.mcastID + " --port=" + self.pon + " --slot=" + self.slot + " --onuID=" + onuid + " --add-onu-port=veip.1 --admin=enable --name=iptv-multicast --serviceID-onu=4"
        add_mcast_pkg = "remote-eq/onu/services/mcast-package/create --onuID=" + onuid + " --port=" + self.pon + " --slot=" + self.slot + " --serviceID-onu=3 --pkg-id=" + self.mcastPKG

        return (create_onu,
                add_mgmt,
                add_pppoe,
                add_igmp,
                add_mcast,
                add_mcast_pkg)

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


if __name__ == "__main__":
    main()

