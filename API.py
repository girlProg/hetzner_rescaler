import requests
import requests
import time
from datetime import datetime, timedelta
import json
import pprint 
import logging
import paramiko
import select
import os

config_file = open(os.path.abspath('config.json'))
config = json.load(config_file)
pp = pprint.PrettyPrinter(indent=4)

api_key = config['api_key']
server_id = config['server_id']
ip_address = config['ip_address']
username = config['username']
password = config['password']

BASE_URL = f'https://api.hetzner.cloud/v1/servers/{server_id}'
headers = {'User-Agent': 'Mozilla/5.0', "Authorization": f"Bearer {api_key}"}

def get_server_metrics():
    yesterday = (datetime.today() - timedelta(hours=1, minutes=30)).isoformat()
    today = datetime.today().isoformat()
    result = requests.get(f'{BASE_URL}/metrics?'
                        f'type=cpu&'
                        f'start={yesterday}&'
                        f'end={today}&' 
                        f'step=100', 
                        headers=headers)
    print(yesterday)
    pp.pprint(json.loads(result.content))


def power_off_server():
    result = requests.post(f'{BASE_URL}/actions/poweroff', headers=headers)
    pp.pprint(json.loads(result.content))
    return result.content


def power_on_server():
    result = requests.post(f'{BASE_URL}/actions/poweron', headers=headers)
    pp.pprint(json.loads(result.content))
    return json.loads(result.content)


def change_server_type(new_server):
    headers['Content-Type'] = 'application/json'
    # upgrade_disk needds to be set to FALSE so that downgrade is possible
    data = {"server_type": new_server,"upgrade_disk": False}
    result = requests.post(f'{BASE_URL}/actions/change_type', headers=headers, data=json.dumps(data))
    # pp.pprint(json.loads(result.content))
    if result.status_code == 201:
        return json.loads(result.content)
    else: 
        return f"There was an error in changing server type: {result.status_code}" 


def get_current_server_type():
    result = requests.get(f'{BASE_URL}', headers=headers)
    logging.info(f"Current server: {json.loads(result.content)['server']['server_type']['name']}")
    return json.loads(result.content)['server']['server_type']['name']


def get_all_server_types():
    result = requests.get(f'https://api.hetzner.cloud/v1/server_types', headers=headers)
    # pp.pprint(json.loads(result.content))
    return json.loads(result.content)

