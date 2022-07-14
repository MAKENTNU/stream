# stream
Stream from Raspberry Pi to Django website with WebSockets.


### Setup
1. Enter the home folder if you are not already there: `cd /home/pi/`
1. Clone this repository: `git clone https://github.com/MAKENTNU/stream.git`
1. Enter the newly created `stream` folder: `cd stream/`

The rest of the steps can be completed by running the setup script `./setup.sh`.
It will ask for the stream name, which can only consist of english letters, numbers, hyphens or underscores.
The secret can be found on locally on the MAKE NTNU server in `local_settings.py` and is called `stream_key`.

The RPi will reboot once the script is done and the stream should now be visible on the website.

The `STREAM_NAME` and `KEY` can be edited manually if needed:
1. Enter stream folder `cd stream`
1. Edit file `nano local_settings.py`
1. `reboot`


The steps that the script does, is described below.

1. Create a virtual environment `sudo virtualenv -p python3 env_stream`
1. Source environment `source env_stream/bin/activate`
1. Install system libraries `sudo apt install libopenjp2-7 libtiff5 libjpeg-dev python3-dev`
1. Install requirements `pip install -r requirements.txt`
1. Deactivate environment `deactivate`
1. Copy service to systemd `sudo cp stream.service /etc/systemd/system/stream.service`
1. Enable service `sudo systemctl enable stream`
1. Start service `sudo systemctl start stream`



Detailed guide of the hardware setup is available on MAKE NTNU's Google Drive.
