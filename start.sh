#!/bin/bash
sudo apt update && sudo apt upgrade -y
apt install ffmpeg -y
python3 -m pip install --upgrade pip
python3 -m pip install -U --pre "yt-dlp[default]"
pip3 install -r requirements.txt
python3 MultiDownloaderv4.0.py &
