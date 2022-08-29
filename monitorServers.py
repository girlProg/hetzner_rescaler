
import time
from datetime import datetime, timedelta
import json
import sys
import pprint  
import diskWriter
import threading
import pandas as pd
import logging
import API
import multiprocessing


proc = multiprocessing.Process(target=diskWriter.write_cpu_usage, args=())
disk_writer_thread = threading.Thread(target=diskWriter.write_cpu_usage)

logging.basicConfig(filename = 'activitylog.log',
                    level = logging.DEBUG,
                    format = '%(asctime)s:%(levelname)s:%(name)s: %(message)s')

config_file = open('config.json')
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

server_types = [ "cx11", "cpx11", "cx21", "cpx21", "cx31", "cpx31", "cx41", "cpX41", "cx51", "cpx51" ]

amd_server_types = [ "cpx11", "cpx21","cpx31", "cpx41", "cpx51" ]
amd_dedicated_server_types = [ "ccx12", "ccx22","ccs32", "ccx42", "ccx52", "ccx62" ]
intel_server_types = [ "cx11", "cx21", "cx31",  "cx41",  "cx51" ]

NEW_SERVER= ''
OLD_SERVER = ''
SHOULD_CHANGE_SERVER = ''

pp = pprint.PrettyPrinter(indent=4)


def get_update_server_name(change_type):
    global NEW_SERVER
    global OLD_SERVER
    global SHOULD_CHANGE_SERVER
    current_server_types = []
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
    global NEW_SERVER
    while True:
        try:
            df = pd.read_csv('cpu_usage.csv')
            aggregat_usage_for_downgrade = df.rolling(min_periods=1, window=downgrade_duration).agg({"CPU": "mean", "RAM": "mean"})
            average_ram_usage = aggregat_usage_for_downgrade['RAM'].mean()
            average_cpu_usage = aggregat_usage_for_downgrade['CPU'].mean()

            logging.info(f'cpu: {average_cpu_usage} ram: {average_ram_usage}. Over the last {downgrade_duration} minutes')
            get_update_server_name('downgrade')
            if average_cpu_usage <= downgrade_percent or average_ram_usage <= downgrade_percent :
                if average_cpu_usage <= downgrade_percent:
                    logging.info(f'Downgrading server from {OLD_SERVER} to {NEW_SERVER} due to CPU usage below {downgrade_percent}% threshold: {average_cpu_usage}%')
                if average_ram_usage <= downgrade_percent:
                    logging.info(f'Downgrading server from {OLD_SERVER} to {NEW_SERVER} due to RAM usage below {downgrade_percent}% threshold: {average_ram_usage}%')
            
                if NEW_SERVER != "" and SHOULD_CHANGE_SERVER == True:
                    API.power_off_server()
                    time.sleep(10)
                    change_server()
                    # logging.info(f'Downgrading server from {OLD_SERVER} to {NEW_SERVER} due to RAM usage below {downgrade_percent}% threshold :{average_ram_usage}%')
                    time.sleep(25)
                    logging.info(API.get_current_server_type())
                    diskWriter.empty_file_contents()
                    NEW_SERVER = ''
                else:
                    logging.error('There was a problem in downgrading server type. Server could be at lowest level')

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
                    API.power_off_server()
                    time.sleep(10)
                    change_server()
                    # logging.info(f'Upgrading server from {OLD_SERVER} to {NEW_SERVER} due to RAM usage above {upgrade_percent}% threshold :{average_ram_usage}%')
                    time.sleep(25)
                    logging.info(API.get_current_server_type())
                    diskWriter.empty_file_contents()
                    NEW_SERVER = ''
                else:
                    logging.error('There was a problem in upgrading server type. Server could be at highest level')

            print(f'cpu: {average_cpu_usage} ram: {average_ram_usage}. Over the last {downgrade_duration} minutes')
        except Exception as e:
            logging.info("No data in the csv file. This happens after a fresh run of the script or after a server change: " + str(e))
        time.sleep(10)




if __name__ == '__main__':
    disk_writer_thread.start()
    should_downgrade_server()

# API.power_off_server()
# API.get_current_server_type()
# x = API.change_server_type('cpx11')
# print(x)
