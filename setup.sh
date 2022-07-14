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
sudo apt install libopenjp2-7 libtiff5 libjpeg-dev python3-dev python3-venv


# Create virtual environment
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
# The `deactivate` command of the `venv` package has an unset variable bug.
# This is fixed in a newer version of Python than 3.7 (which is the version that currently comes with OctoPi),
# but let's delay the hassle of upgrading until later :))
set +u
deactivate
set -u


# Set up and start service
sudo ln -s "$(pwd)/stream.service" /etc/systemd/system/stream.service
sudo systemctl enable stream
sudo systemctl start stream

sudo reboot
