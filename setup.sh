#!/bin/bash
set -euo pipefail

# Enable camera
sudo raspi-config nonint do_camera 0


# Read input
read -p "Enter stream name: " stream
echo -n "Enter secret: "
read -sr secret
echo

echo "STREAM_NAME = '$stream'" > local_settings.py
echo "KEY = '$secret'" >> local_settings.py


# Install dependencies
sudo apt install libopenjp2-7 libtiff5 libjpeg-dev python3-dev


# Create virtual environment
sudo apt install virtualenv
virtualenv -p python3 env_stream
source env_stream/bin/activate
pip install -r requirements.txt
deactivate


# Set up and start service
sudo cp stream.service /etc/systemd/system/stream.service
sudo systemctl enable stream
sudo systemctl start stream

sudo reboot
