#!/usr/bin/python

import mymod
import shutil
import re
from creds import *

TFTP = '192.168.1.1'
OLTS = [olt_nova_mytna, olt_shc3, olt_dc4]

def main():

    for olt in OLTS:
        myolt = mymod.Olt(olt)
        ssh = myolt.connect()
        remote_conn = ssh.invoke_shell()
        myolt.send_command(remote_conn)

        backups = myolt.find_bck(remote_conn)

        create_bck = "backup-manager/create --description=auto-backup"

        if backups:
            if len(backups) >= 10:

                #delete first backup from flash on OLT to free space (max 10 files allowed)
                delete_bck = "backup-manager/remove --local-file=" + backups[0]
                myolt.send_command(remote_conn, delete_bck)
            else:
                pass

        #create new backup
        myolt.send_command(remote_conn, create_bck)
        [myolt.send_command(remote_conn) for i in range(3)]

        last_bck = myolt.find_bck(remote_conn)[-1]

       #upload to TFTP server
        download_bck = "backup-manager/export --local-file=" + last_bck + " --server-ip=" + TFTP + " --server-port=69"
        myolt.send_command(remote_conn, download_bck)

        src_file = "/srv/tftp/" + last_bck
        dst_file = "/home/rancid/olt/me4600-olt/backup/" + last_bck

        print "Copping file %s to backup directory\n" % last_bck
        try:
            shutil.copyfile(src_file, dst_file)
            print "Copy OK"
        except:
            print "Copy Error"

        remote_conn.close()

if __name__ == "__main__":
    main()

