#!/usr/bin/env bash

if [[ ! -d venv ]]; then
    python3 -m venv venv
fi

if [[ ! -f venv/.done ]]; then
    ./venv/bin/pip install -r requirements.txt
    touch venv/.done
fi

./venv/bin/python3 server.py