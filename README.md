# stream
Steam from Raspberry Pi to Django website with WebSockets


### Setup
1. Enable camera interface `sudo raspi-config`
2. Enter user folder `cd /home/pi`
3. Clone repo `git clone https://github.com/MAKENTNU/stream.git`
4. Enter stream folder `cd stream`
5. Add local settings `nano local_settings.py`
6. Create a virtual environment `virtualenv -p python3 env_stream`
7. Source environment `source env_stream/bin_activate`
8. Install requirements `pip install -r requirements.txt`
9. Deactivate environment `deactivate`
10. Copy service to systemd `sudo cp stream.service /etc/systemd/system/stream.service`
11. Enable service `sudo systemctl enable stream`
12. Start service `sudo systemctl start stream`
