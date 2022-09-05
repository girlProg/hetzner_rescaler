import time
from datetime import datetime
import json
import pprint  
import threading
import pandas as pd
import logging
import API
import paramiko
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(filename = 'activitylog.log',
                    level = logging.INFO,
                    format = '%(asctime)s:%(levelname)s:%(name)s: %(message)s')

config_file = open(os.path.join(ROOT_DIR, 'config.json'))
config = json.load(config_file)

api_key = config['api_key']
ip_address = config['ip_address']
username = config['username']
password = config['password']
server_name = config['server_name']
server_id = config['server_id']
downgrade_percent = int(config['downgrade_percent'])
downgrade_duration = int(config['downgrade_duration'])
upgrade_percent = int(config['upgrade_percent'])
upgrade_duration = int(config['upgrade_duration'])
frequency = int(config['frequency'])

server_types = [ "cx11", "cpx11", "cx21", "cpx21", "cx31", "cpx31", "cx41", "cpX41", "cx51", "cpx51" ]

amd_server_types = [ "cpx11", "cpx21","cpx31", "cpx41", "cpx51" ]
amd_dedicated_server_types = [ "ccx12", "ccx22","ccs32", "ccx42", "ccx52", "ccx62" ]
intel_server_types = [ "cx11", "cx21", "cx31",  "cx41",  "cx51" ]

NEW_SERVER= ''
OLD_SERVER = ''
SHOULD_CHANGE_SERVER = ''
DISK_WRITER_PID = 0
should_write_to_file = True

pp = pprint.PrettyPrinter(indent=4)
current_server_types = []

def checkIfMidnight():
    now = datetime.now()
    seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    return seconds_since_midnight < 150

def get_remote_usage():
    try:
        HOST=ip_address
        COMMAND_VM=  " free | grep Mem | awk '{print $3/$2 * 100.0}' && echo \" \"$[100-$(vmstat 1 2|tail -1|awk '{print $15}')]\"\""

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip_address, 22,  username, password, timeout=3)

        stdin, stdout, stderr = ssh.exec_command(COMMAND_VM, timeout=3)
        while int(stdout.channel.recv_exit_status()) != 0:
            time.sleep(1)
        usage =  stdout.read().decode()
        ssh.close()
        return usage
    except Exception as e:
        write_cpu_usage()
        

# this is necessary with every server downgrade or upgrade
def empty_file_contents():
    f = open("cpu_usage.csv", "w")
    f.write('Number,Time,CPU,RAM\n')
    f.close()


def write_cpu_usage():
    global should_write_to_file
    f = open("cpu_usage.csv", "w")
    f.write(f"Number,Time,CPU,RAM\n")
    logging.info("Writing to file started")
    timer = 1
    while not checkIfMidnight():
        if should_write_to_file:
            usage = get_remote_usage()
            if usage:
                ram_usage = usage.split('\n')[0]
                cpu_usage = usage.split('\n')[1]
                
                f.write(f"{timer}, {datetime.now()}, {cpu_usage}, {ram_usage} \n")
                f.flush()
                timer = timer + 1
                time.sleep(frequency) #sleep for the config duration in seconds
            

def get_update_server_name(change_type):
    global NEW_SERVER
    global OLD_SERVER
    global SHOULD_CHANGE_SERVER
    global current_server_types
    
    current_server = API.get_current_server_type()
    SHOULD_CHANGE_SERVER = True
    if 'ccx' in current_server:
        current_server_types = amd_dedicated_server_types
    elif 'cpx' in current_server:
        current_server_types = amd_server_types
    else:
        current_server_types = intel_server_types

    x = current_server_types.index(current_server)
    if change_type == 'upgrade': 
        if current_server == current_server_types[-1]:
            SHOULD_CHANGE_SERVER = False
            return 'cannot upgrade server, already at higest server'
        else:
            upgrade_server_name = current_server_types[x+1]
            NEW_SERVER = upgrade_server_name.upper()
            OLD_SERVER = current_server.upper()
            return upgrade_server_name
    elif change_type == 'downgrade':
        if current_server == current_server_types[0]:
            SHOULD_CHANGE_SERVER = False
            return 'cannot downgrade server, already at lowest server'
        else:
            downgrade_server_name = current_server_types[x-1]
            NEW_SERVER = downgrade_server_name.upper()
            OLD_SERVER = current_server.upper()
            return downgrade_server_name

def change_server():
    global NEW_SERVER
    logging.info(API.change_server_type(NEW_SERVER.lower()))

def should_downgrade_server():
    empty_file_contents()
    global NEW_SERVER
    global current_server_types
    global should_write_to_file
    while not checkIfMidnight:
        try:
            df = pd.read_csv('cpu_usage.csv')
            aggregat_usage_for_downgrade = df.rolling(min_periods=1, window=downgrade_duration).agg({"CPU": "mean", "RAM": "mean"})
            average_ram_usage = aggregat_usage_for_downgrade['RAM'].mean()
            average_cpu_usage = aggregat_usage_for_downgrade['CPU'].mean()

            logging.info(f'cpu: {average_cpu_usage} ram: {average_ram_usage}. Over the last {downgrade_duration} minutes')
            server_name = get_update_server_name('downgrade')
            # if server_name != current_server_types[1]:
                # print(server_name + current_server_types[0])
                # only downgrade if the server is downgradable
            if 'cannot' not in server_name:
                if average_cpu_usage <= downgrade_percent or average_ram_usage <= downgrade_percent :
                    if average_cpu_usage <= downgrade_percent:
                        logging.info(f'Downgrading server from {OLD_SERVER} to {NEW_SERVER} due to CPU usage below {downgrade_percent}% threshold: {average_cpu_usage}%')
                    if average_ram_usage <= downgrade_percent:
                        logging.info(f'Downgrading server from {OLD_SERVER} to {NEW_SERVER} due to RAM usage below {downgrade_percent}% threshold: {average_ram_usage}%')
                
                    if NEW_SERVER != "" and SHOULD_CHANGE_SERVER == True:
                        should_write_to_file = False
                        API.power_off_server()
                        time.sleep(10)
                        change_server()
                        time.sleep(25)
                        logging.info(API.get_current_server_type())
                        empty_file_contents()
                        should_write_to_file = True
                        NEW_SERVER = ''
                    else:
                        logging.info('There was a problem in downgrading server type. Server could be at lowest level')
                else:
                    logging.info(server_name)

            aggregat_usage_for_upgrade = df.rolling(min_periods=1, window=upgrade_duration).agg({"CPU": "mean", "RAM": "mean"})
            average_ram_usage = aggregat_usage_for_upgrade['RAM'].mean()
            average_cpu_usage = aggregat_usage_for_upgrade['CPU'].mean()
            get_update_server_name('upgrade')
            if average_cpu_usage >= upgrade_percent or average_ram_usage >= upgrade_percent :
                if average_cpu_usage >= upgrade_percent:
                    logging.info(f'Upgrading server from {OLD_SERVER} to {NEW_SERVER} due to CPU usage above {upgrade_percent}% threshold: {average_cpu_usage}%')
                if average_ram_usage >= upgrade_percent:
                    logging.info(f'Upgrading server from {OLD_SERVER} to {NEW_SERVER} due to RAM usage above {upgrade_percent}% threshold: {average_ram_usage}%')
                if NEW_SERVER != "" and SHOULD_CHANGE_SERVER == True:
                    should_write_to_file = False
                    API.power_off_server()
                    time.sleep(10)
                    change_server()
                    time.sleep(25)
                    logging.info(API.get_current_server_type())
                    empty_file_contents()
                    should_write_to_file = True 
                    NEW_SERVER = ''
                else:
                    logging.error('There was a problem in upgrading server type. Server could be at highest level')

            print(f'cpu: {average_cpu_usage} ram: {average_ram_usage}. Over the last {downgrade_duration} minutes')
        except Exception as e:
            logging.info("No data in the csv file. This happens after a fresh run of the script or after a server change: " + str(e))
        time.sleep(frequency)




if __name__ == '__main__':
    disk_writer_thread = threading.Thread(target=write_cpu_usage)
    disk_writer_thread.start()      
    should_downgrade_server()
