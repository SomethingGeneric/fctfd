#!/usr/bin/env bash

# git pull

[[ -f /etc/systemd/system/ctfscoreboard.service ]] && systemctl disable --now ctfscoreboard && rm /etc/systemd/system/ctfscoreboard.service

[[ ! -d venv ]] && python3 -m venv venv
./venv/bin/pip install -r requirements.txt

my_pwd=$(pwd)
user=$(whoami)

cp ctfscoreboard.service.ex ctfscoreboard.service
sed -i "s/MYPWD/${my_pwd//\//\\/}/g" ctfscoreboard.service
sed -i "s/UNAME/${user}/g" ctfscoreboard.service

cp ctfscoreboard.service /etc/systemd/system/ctfscoreboard.service
systemctl daemon-reload
systemctl enable --now ctfscoreboard

if [[ ! -d db ]]; then
    ./venv/bin/python3 create_data.py
fi

echo "all done."
