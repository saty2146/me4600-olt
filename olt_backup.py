#!/usr/bin/python

import mymod
import StringIO
import argparse
import datetime
import sys
import shutil

date = datetime.datetime.today().strftime('%Y-%m-%d')

user = 'admin'
passwd = 'admin'
hostname = '192.168.35.50'
tftp = '192.168.1.100'

def find_bck(remote_conn,position='last'):

    cmd = 'backup-manager/show'
    output = mymod.send_command(remote_conn, cmd)

    buf=StringIO.StringIO(output)

    line = buf.read().split("\n")
    
    last_row = line[-3].split('|')
    first_row = line[6].split('|')

    last_row = map(str.strip, last_row)
    first_row = map(str.strip, first_row)

    last_bck = last_row[1]
    first_bck = first_row[1]

    return (last_bck, first_bck)

def main():
    
    ssh = mymod.connect(hostname, user, passwd)
    # Use invoke_shell to establish an 'interactive session'
    remote_conn = ssh.invoke_shell()
    print "Interactive SSH session established to %s\n" % hostname
    mymod.send_command(remote_conn)
    create_bck = "backup-manager/create --description=auto-backup"
    output = mymod.send_command(remote_conn, create_bck)
    [mymod.send_command(remote_conn) for i in range(3)]
    last_bck, first_bck = find_bck(remote_conn)    
    
    download_bck = "backup-manager/export --local-file=" + last_bck + " --server-ip=" + tftp + " --server-port=69"
    mymod.send_command(remote_conn, download_bck)
    
    delete_bck = "backup-manager/remove --local-file=" + first_bck
    mymod.send_command(remote_conn, delete_bck)
    
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

