[Unit]
Description=HP Scoreboard Service
After=network.target

[Service]
WorkingDirectory=MYPWD
Environment="PATH=MYPWD/venv/bin"
ExecStart=MYPWD/venv/bin/python /home/matt/Documents/hpscoreboard/server.py
Restart=always

[Install]
WantedBy=multi-user.target
