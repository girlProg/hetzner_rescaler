import logging
import psutil
import time
import datetime
import paramiko
import json

config_file = open('config.json')
config = json.load(config_file)

ip_address = config['ip_address']
username = config['username']
password = config['password']

# with every run of the script, this file is rewritten
def get_remote_usage():
    HOST=ip_address
    COMMAND_VM=  " free | grep Mem | awk '{print $3/$2 * 100.0}' && echo \" \"$[100-$(vmstat 1 2|tail -1|awk '{print $15}')]\"\""

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip_address, 22,  username, password, timeout=10)

    stdin, stdout, stderr = ssh.exec_command(COMMAND_VM)
    while int(stdout.channel.recv_exit_status()) != 0:
        time.sleep(1)
    # print(f"Output: {}")
    usage =  stdout.read().decode()
    return usage

    

def write_cpu_usage():
    f = open("cpu_usage.csv", "w")
    f.write(f"Number,Time,CPU,RAM\n")
    logging.info("Writing to file started")
    timer = 1
    while True:
        usage = get_remote_usage()
        ram_usage = usage.split('\n')[0]
        cpu_usage = usage.split('\n')[1]
        
        f.write(f"{timer}, {datetime.datetime.now()}, {cpu_usage}, {ram_usage} \n")
        f.flush()
        timer = timer + 1
        time.sleep(2) #slee for 60 seconds
        


# this is necessary with every server downgrade or upgrade
def empty_file_contents():
    f = open("cpu_usage.csv", "w")
    f.write('Number,Time,CPU,RAM\n')
    f.close()