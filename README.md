# FCTFD

Free CTF Daemon

Python Flask app for CTF-style events

## Setup
* Install python3, python3-venv, and git
* Clone repo 
* Put your favorite admin password (not encrypted!!) into `db/admin.pass`
* Run `./run.sh` if you're on Mac/Linux, or otherwise simply:
```
python -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python server.py
```

## Run with systemd
Just run `./install.sh` (after cloning repo and setting `admin.pass`)

## Utils
If you want to bulk create teams/challenges instead of the webUI, you can use `create_data.py` (which you should prefix with `./venv/bin/python` if you used `run.sh` or `install.sh`)