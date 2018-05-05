import io
import time
import picamera
import threading
import json
from base64 import b64encode
from datetime import datetime
from websocket import create_connection
from websocket._exceptions import WebSocketBadStatusException, WebSocketConnectionClosedException
from PIL import Image
from io import BytesIO

# Default settings
RESOLUTION = (640, 480)
IP = '127.0.0.1'
PORT = 80
KEY = 'SECRET'
STREAM_NAME = 'STREAM'
DEBUG = True
VFLIP = False
HFLIP = False
THREADS = 3
DELAY = 0
QUALITY = 70


# Override defaults with local_settings
try:
    from local_settings import *
except ImportError:
    pass


def debug(*args):
    if DEBUG:
        print(datetime.now(), *args)


def read(ws):
    while True:
        try:
            ws.recv()
        except:
            break


def decode_and_send(ws, image):
    result = ws.send(json.dumps({
       'image': b64encode(image).decode('ascii'),
       'key': KEY,
    }))
    debug('Send from', threading.current_thread().name)
    return result


def sender(images, cv, error):
    try:
        ws = create_connection('wss://%s/ws/stream/%s/' % (IP, STREAM_NAME))
        threading.Thread(target=read, args=(ws,)).start()
        while not error[0]:
            with cv:
                while not len(images):
                    if error[0]: return
                    cv.wait()
                image = images.pop(0)
            decode_and_send(ws, image)
    except:
        debug('Unable to connect')
        error[0] = True
        with cv:
            cv.notify_all()


def capture():
    debug('Connecting to %s on port %s' % (IP, PORT))

    cv = threading.Condition()
    stream_capture = BytesIO()
    stream_image = BytesIO()
    images = []
    error = [False]

    if not THREADS:
        try:
            ws = create_connection('wss://%s/ws/stream/%s/' % (IP, STREAM_NAME))
            threading.Thread(target=read, args=(ws,)).start()
        except:
            debug('Unable to connect')
            return

    for _ in range(THREADS):
        threading.Thread(target=sender, args=(images, cv, error)).start()

    with picamera.PiCamera() as camera:
        camera.resolution = RESOLUTION
        camera.vflip = VFLIP
        camera.hflip = HFLIP

        for _ in camera.capture_continuous(stream_capture, 'jpeg', use_video_port=True):
            time.sleep(DELAY)
            debug('Capture')
            debug('Active threads:', threading.active_count())
            stream_capture.seek(0)
            stream_image.seek(0)
            stream_image.truncate()
            Image.open(stream_capture).save(stream_image, 'jpeg', optimize=True, quality=QUALITY)
            if THREADS:
                if error[0]:
                    break
                with cv:
                    if len(images) < 3:
                        images.append(stream_image.getvalue())
                    cv.notify_all()
            else:
                try:
                    decode_and_send(ws, stream_image.getvalue())
                except:
                    return
            stream_capture.seek(0)
            stream_capture.truncate()


def main():
    while True:
        capture()
        time.sleep(3)


main()
