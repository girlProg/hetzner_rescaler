# Hetzner Server Auto-rescaling Script Instructions

# Adding a new Server Monitor to Test Server

To add another Server Changing Script to the ‘test’ server, run the commands below after logging into the server via ssh

`git clone https://github.com/girlProg/hetzner_rescaler.git <new_server_name>`

you will need to change `<new_server_name>` to the name you would like the new folder to be called. Make sure to name it something you can remember in reference to what the Server does. This will be more important when you have 10 server monitor scripts running and you need to check the logs of a particular server.  Run the next commands

`touch config.json`

`nano config.json`

This will open a text editor, paste the below: (make sure you change the IP address, username and password and any other configurations you want)

```python
{
  "api_key": "PASTE API KEY HERE",
  "ip_address": "IP ADDRESS HERE",
  "username": "root",
  "password": "PASTE PASSWORD HERE",
  "server_name": "SERVER NAME HERE",
  "server_id": "SERVER ID",
  "downgrade_percent": "30",
  "downgrade_duration": "30",
  "upgrade_percent": "50",
  "upgrade_duration": "3",
  "frequency": "60"
}
```

to exit, press `CTRL + X`, then `Y` and press enter

PLEASE NOTE: Everything needs to be in double quotes in the config file.

In the command line, enter 

`crontab -e`

![Screenshot 2022-09-06 at 00.21.40.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/1e01958c-86f7-41e1-b2e9-f451d0f01ead/Screenshot_2022-09-06_at_00.21.40.png)

this will open a file that runs the script every day.
go to the bottom using arrows, and enter this line

`0 0 * * * python3 /root/<new_server_name>/monitorServers.py`

Make sure to change the `<new_server_name>` to the new directory name you created earlier.

To exit, press `CTRL + X`, then `Y` and press enter

And youre done!

The server will run at midnight everyday continously.

# Monitoring a Server

ssh into the test server and enter into the Server Monitor directory 

eg:  `cd hetzner_server_changer`

(can also be `cd <new_server_name>`)

then type: `tail -f activitylog.log`

This will show you all server activity and the most recent time it was active. 

You can keep this terminal window for as long as you would like.

To exit, press `CTRL + C`

# Changing server to be monitored by script

ssh into the test server and enter into the Server Monitor directory 

`nano config.json`

you will see something like this:

![Screenshot 2022-09-06 at 00.32.30.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/93311a1b-3d23-4b8f-aaec-76834c61f872/Screenshot_2022-09-06_at_00.32.30.png)

use the arrow keys to change the `ip address, password, username` and `server_id` to the correct parameters that belong to the new server.

To exit, press `CTRL + X`, then `Y` to save and exit, then and press enter 

# Updating the Script

If a change has been made to the script to make it better there is an easy way to update it. 

For each server being monitored, the instruction below has to be done for each folder.

`git pull`

once you do this, any new updates to the script will immediately take effect.