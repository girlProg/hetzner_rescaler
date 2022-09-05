to run inside a venv:

`python3 -m pip install virtualenv`

`virtualenv venv`

`source bin/activate`

`apt install python3-pip`

`pip install requirements.txt` 

`touch config.json`

`vi config.json`

paste the below

```
{
  "api_key": "LKmDgZDlGVLfi9FtmTr3RziZjqZMGQGprbgnSPwAf8YjtX7XEGoCVbLk1s4mMDUH",
  "ip_address": "5.161.150.87",
  "username": "root",
  "password": "bxhux9CF9TJnkqEh7upH455",
  "server_name": "test",
  "server_id": "23284466",
  "downgrade_percent": "30",
  "downgrade_duration": "30",
  "upgrade_percent": "50",
  "upgrade_duration": "3",
  "frequency": "60"
}
```

enter `:wq` followed by the return key to exit