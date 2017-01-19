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
            results.hostname,
	    results.tftp)


def find_bck(remote_conn,position='last'):

    cmd = 'backup-manager/show'
    output = mymod.send_command(remote_conn, cmd)

    buf=StringIO.StringIO(output)

    line = buf.read().split("\n")
    
    if position == 'last':
    	row = line[-3].split('|')
    else:
    	row = line[6].split('|')
	
    row = map(str.strip, row) 
    file_bck = row[1]
    
    return file_bck


def main():
    
    user, passwd, hostname, tftp = check_arg(sys.argv[1:])
    
    ssh = mymod.connect(hostname, user, passwd)
    # Use invoke_shell to establish an 'interactive session'
    remote_conn = ssh.invoke_shell()
    print "Interactive SSH session established to %s\n" % hostname
    mymod.send_command(remote_conn)
    create_bck = "backup-manager/create --description=auto-backup"
    output = mymod.send_command(remote_conn, create_bck)
    [mymod.send_command(remote_conn) for i in range(3)]
    last_bck = find_bck(remote_conn)
    download_bck = "backup-manager/export --local-file=" + last_bck + " --server-ip=" + tftp + " --server-port=69"
    mymod.send_command(remote_conn, download_bck)
    
    first_bck = find_bck(remote_conn, 'first')
    delete_bck = "backup-manager/remove --local-file=" + first_bck
    mymod.send_command(remote_conn, delete_bck)



if __name__ == "__main__":
    main()

