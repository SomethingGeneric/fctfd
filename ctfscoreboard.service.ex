[Unit]
Description=CTF Scoreboard Service
After=network.target

[Service]
WorkingDirectory=MYPWD
Environment="PATH=MYPWD/venv/bin"
ExecStart=MYPWD/venv/bin/python MYPWD/server.py prod
Restart=always
User=UNAME
Group=UNAME

[Install]
WantedBy=multi-user.target
