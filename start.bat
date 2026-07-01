@echo off
python.exe -m pip install --upgrade pip
python -m pip install -U --pre "yt-dlp[default]"
pip install -r  requirements.txt
start python MultiDownloaderv4.0.py


