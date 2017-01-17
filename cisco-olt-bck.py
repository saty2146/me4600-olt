#!/usr/bin/python

import mymod
import StringIO
import argparse
import datetime
import sys

date = datetime.datetime.today().strftime('%Y-%m-%d')
filename = 'autobck_' + str(date)

def check_arg(args=None):

    parser = argparse.ArgumentParser(description='Cisco OLT backuper')
    maingroup = parser.add_argument_group(title='required')
    maingroup.add_argument('-u', '--user',
                        help='OLT username',
                        default='admin')
    maingroup.add_argument('-p', '--passwd',
                        help='OLT password',
                        required='True')
    maingroup.add_argument('-H', '--hostname',
			help='Hostname',
			required='True')
    maingroup.add_argument('-t', '--tftp',
                        help='TFTP server address',
                        required='True')

    results = parser.parse_args(args)

    return (results.user,
            results.passwd,
            results.hostname)


def find_last_bck(remote_conn):

    cmd = 'backup-manager/show'
    output = mymod.send_command(remote_conn, cmd)

    buf=StringIO.StringIO(output)

    line = buf.read().split("\n")
   # for i in line:
   #	print i
    row = line[-3].split('|')
    file_bck = row[1]
    #print file_bck
    
    return file_bck


def main():
    
    user, passwd, hostname = check_arg(sys.argv[1:])
    
    ssh = mymod.connect(hostname, user, passwd)
    # Use invoke_shell to establish an 'interactive session'
    remote_conn = ssh.invoke_shell()
    print "Interactive SSH session established to %s\n" % hostname
    mymod.send_command(remote_conn,"\n")
    #create_bck = "backup-manager/create --description=auto-backup"
    #mymod.send_command(remote_conn, create_bck)
    lastbck = find_last_bck(remote_conn)
    download_bck = "backup-manager/export --local-file=" + lastbck + " --server-ip=X.X.X.X --server-port=69"
    mymod.send_command(remote_conn, download_bck)


if __name__ == "__main__":
    main()

