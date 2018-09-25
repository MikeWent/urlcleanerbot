#!/bin/bash

name="urlcleanerbot"

sudo systemctl stop "$name.service" 2> /dev/null # hide output if service doesn't exist

echo "[Unit]
Description=URL cleaner Telegram bot
Documentation=https://github.com/MikeWent/urlcleanerbot
Wants=network-online.target
After=network.target network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 $PWD/urlcleanerbot.py
Restart=always
RestartSec=5
User=$USER
WorkingDirectory=$PWD

[Install]
WantedBy=multi-user.target" > $name.service

sudo mv $name.service /lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable "$name.service"
sudo systemctl start "$name.service"
echo "Service '$name.service' started and enabled on startup"
