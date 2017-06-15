#!/usr/bin/python

import mymod

def main():

    olt, profile, sn = mymod.olt_profile(mymod.check_arg)

    if sn is not None:
        myolt = mymod.Olt(olt, profile)
        ssh = myolt.connect()
        remote_conn = ssh.invoke_shell()
        myolt.send_command(remote_conn)

        onu_id, profile_id = myolt.find_onu_id(remote_conn, sn)
        cl_srv = myolt.find_onu_services(remote_conn, onu_id)
        
        print ("Deleting services ...")
        for srv_id in reversed(sorted(cl_srv.keys())):
            print srv_id
            myolt.remove_onu_service(remote_conn, onu_id, srv_id)

        print ("Removing ONU ...")
        myolt.remove_onu(remote_conn, onu_id)

        remote_conn.close()
    else:
        print ("!!!No ONU SN specified!!!")

if __name__ == "__main__":
    main()
