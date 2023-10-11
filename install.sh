#!/usr/bin/env bash

git pull

[[ -f /etc/systemd/system/hpscoreboard.service ]] && systemctl disable --now hpscoreboard && rm /etc/systemd/system/hpscoreboard.service

[[ ! -d venv ]] && python3 -m venv venv
./venv/bin/pip install -r requirements.txt

my_pwd=$(pwd)

cp hpscoreboard.service.ex hpscoreboard.service
sed -i "s/MYPWD/${my_pwd//\//\\/}/g" hpscoreboard.service

cp hpscoreboard.service /etc/systemd/system/hpscoreboard.service
systemctl daemon-reload
systemctl enable --now hpscoreboard

if [[ ! -d db ]]; then
    ./venv/bin/python3 create_data.py
fi

echo "all done."