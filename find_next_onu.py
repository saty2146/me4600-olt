#!/usr/bin/python

import mymod

def main():
    
    olt, profile, sn, loc = mymod.olt_profile(mymod.check_arg)
    myolt = mymod.Olt(olt, profile)
    ssh = myolt.connect()
    remote_conn = ssh.invoke_shell()
    myolt.send_command(remote_conn)
    output = myolt.find_next_onu(remote_conn)
    print "Next ONU ID: " + str(output)

    remote_conn.close()

if __name__ == "__main__":
    main()
