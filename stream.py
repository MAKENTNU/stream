import io
import time
import picamera
import threading
import json
from base64 import b64encode
from websocket import create_connection
from datetime import datetime


# Default settings
RESOLUTION = (640, 480)
IP = '127.0.0.1'
PORT = 80
KEY = 'SECRET'
STREAM_NAME = 'STREAM'
DEBUG = True
VFLIP = False
HFLIP = False
MAX_THREADS = 3

# Override defaults with local_settings
try:
    from local_settings import *
except ImportError:
    pass


def send(stream):
    stream[0].seek(0)
    image = b64encode(stream[0].read()).decode('ascii')
    stream[1].send(json.dumps({
        'image': image,
        'key': KEY,
    }))
    stream[2] = True

def capture():
    if DEBUG:
    	print(datetime.now(), 'Connecting to %s on port %s' % (IP, PORT))

    streams = [[io.BytesIO(), create_connection('wss://%s/ws/stream/%s/' % (IP, STREAM_NAME)), True] for _ in range(MAX_THREADS)]
    stream_index = 0

    try:
        with picamera.PiCamera() as camera:
            camera.resolution = RESOLUTION
            camera.vflip = VFLIP
            camera.hflip = HFLIP
            camera.start_preview()
            time.sleep(2)

            while True:
                while not streams[stream_index][2]: pass
                streams[stream_index][2] = False
                streams[stream_index][0].seek(0)
                streams[stream_index][0].truncate()
                camera.capture(streams[stream_index][0], 'jpeg', use_video_port=True)
                if DEBUG:
                    print(datetime.now(), stream_index)
                threading.Thread(target=send, args=(streams[stream_index],)).start()
                stream_index = (stream_index + 1) % MAX_THREADS
    finally:
        for stream in streams:
            stream[1].close()


def main():
    while True:
        try:
            capture()
        except:
            time.sleep(1)


main()
