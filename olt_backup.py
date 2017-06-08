#!/usr/bin/python

import mymod
import StringIO
import argparse
import datetime
import sys
import shutil
import re

user = 'admin'
passwd = 'XXX'
hostname = '192.168.35.51'
tftp = '192.168.35.51'

def find_bck(remote_conn):

    cmd = 'backup-manager/show'
    output = mymod.send_command(remote_conn, cmd)
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

def main():
    
    ssh = mymod.connect(hostname, user, passwd)
    remote_conn = ssh.invoke_shell()
    mymod.send_command(remote_conn)

    backups = find_bck(remote_conn)

    create_bck = "backup-manager/create --description=auto-backup"

    if backups:
        if len(backups) >= 10:

            #delete first backup
            delete_bck = "backup-manager/remove --local-file=" + backups[0]
            mymod.send_command(remote_conn, delete_bck)
        else:
            pass

        #create new backup
        mymod.send_command(remote_conn, create_bck)
        [mymod.send_command(remote_conn) for i in range(3)]

    last_bck = find_bck(remote_conn)[-1]

   #upload to TFTP server 
    download_bck = "backup-manager/export --local-file=" + last_bck + " --server-ip=" + tftp + " --server-port=69"
    mymod.send_command(remote_conn, download_bck)
    
    src_file = "/srv/tftp/" + last_bck
    dst_file = "/home/rancid/olt/me4600-olt/backup/" + last_bck
    
    print "Copping file %s to backup directory\n" % last_bck
    try:
	shutil.copyfile(src_file, dst_file)
	print "OK"
    except:
	print "Error"

    remote_conn.close()

if __name__ == "__main__":
    main()

