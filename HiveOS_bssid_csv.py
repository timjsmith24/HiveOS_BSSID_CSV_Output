#!/usr/bin/python3
import time
import datetime
import sys
import logging
import os
import csv
import paramiko
import multiprocessing
import textfsm

from paramiko.ssh_exception import AuthenticationException, SSHException, BadHostKeyException

logging.getLogger("paramiko").setLevel(logging.WARNING)

PATH = os.path.dirname(os.path.abspath(__file__))
os.environ["NET_TEXTFSM"]='{}/templates/'.format(PATH)


username = 'admin'
password = 'Extreme123!'

outputFile = 'AP_bssids.csv'

cmd = 'show interface'
templateraw = 'hiveos_show_interface.template'

# Git Shell Coloring - https://gist.github.com/vratiu/9780109
RED   = "\033[1;31m"  
BLUE  = "\033[1;34m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"

def csv_import(filename):
    device_list = []
    with open(filename, "r",encoding='utf-8-sig') as file:
        reader = csv.reader(file, delimiter=",")
        # Build list of location dictionaries
        for row in reader:
            #location dictionary
            deviceip , deviceport = row
            device_list.append(tuple([deviceip, deviceport]))
        return device_list

def ap_ssh(ip,port,mp_queue):
    msg = ''
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print (f"Establishing Connection with {ip}:{port}")
        ssh.connect(ip,port = port, username = username , password = password ,timeout=10)
        chan = ssh.invoke_shell()
    except AuthenticationException:
        sys.stdout.write(RED)
        sys.stdout.write("Authentication failed on " + ip + ", please verify your credentials:\n")
        sys.stdout.write(RESET)
    except SSHException as sshException:
        sys.stdout.write(RED)
        sys.stdout.write("Unable to establish SSH connection on " + ip + ": %s\n" % sshException)
        sys.stdout.write(RESET)
    except BadHostKeyException as badHostKeyException:
        sys.stdout.write(RED)
        sys.stdout.write("Unable to verify server's host key on " + ip + ": %s\n" % badHostKeyException)
        sys.stdout.write(RESET)
    except Exception as e:
        sys.stdout.write(RED)
        sys.stdout.write("Operation error on " + ip + ": %s\n" % e)	
        sys.stdout.write(RESET)
    else:
        time.sleep(1)
        x = chan.recv(9999)
        resp = x.decode("utf-8").splitlines()
        devicename = resp[-1].replace('#', '')
        chan.send('console page 0\n')
        time.sleep(1)
        resp = chan.recv(9999)
        chan.send(cmd+'\n')
        time.sleep(1)
        x = chan.recv(99999)
        output = x.decode("utf-8") 
        #print(devicename, output)
        with open('{}/templates/{}'.format(PATH,templateraw), 'r') as f:
            test_template = textfsm.TextFSM(f)
        test_config = test_template.ParseText(output)
        parsed = [dict(zip(test_template.header, row)) for row in test_config]
        for int in parsed:
            if 'Wifi' in int["NAME"]:
                mp_queue.put(f'{devicename},{int["NAME"]},{int["STATE"]},{int["MAC"]},{int["SSID"]}')
    ssh.close()


def main():
    msg = 'AP NAME, INTERFACE, STATE, BSSID, SSID\n'
    filename = 'ip_list.csv'
    device_list = csv_import(filename)
    sizeofbatch = 50
    for i in range(0, len(device_list), sizeofbatch):
        batch = device_list[i:i+sizeofbatch]
        mp_queue = multiprocessing.Queue()
        processes = []
        for deviceip, deviceport in batch:
            p = multiprocessing.Process(target=ap_ssh,args=(deviceip, deviceport, mp_queue))
            processes.append(p)
            p.start()
        for p in processes:
            try:
                p.join()
                p.terminate()
            except:
                print("Error occurred in thread")
        mp_queue.put('STOP')
        for line in iter(mp_queue.get, 'STOP'):
            msg += f"{line}\n"

    
    with open("{}/{}".format(PATH,outputFile), 'w') as f:
        f.write(msg)
    print("Completed. Please look at {} for results".format(outputFile))
if __name__ == '__main__':
    main()