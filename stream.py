import json
import threading
import time
from base64 import b64encode
from datetime import datetime
from io import BytesIO

import picamera
from PIL import Image
from websocket import create_connection


# Default settings
RESOLUTION = (640, 480)
HOST = 'makentnu.no'
KEY = 'SECRET'
STREAM_NAME = 'STREAM'
STREAM_URL = f'wss://{HOST}/ws/stream/{STREAM_NAME}/'
DEBUG = True
VFLIP = False
HFLIP = False
THREADS = 3
DELAY = 0
TIME_BETWEEN_CONNECTION_RETRIES = 3
QUALITY = 50

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
    debug("Send from", threading.current_thread().name)
    return result


def sender(images, cv, error):
    try:
        ws = create_connection(STREAM_URL)
        threading.Thread(target=read, args=(ws,)).start()
        while not error[0]:
            with cv:
                while not len(images):
                    if error[0]:
                        return
                    cv.wait()
                image = images.pop(0)
            decode_and_send(ws, image)
    except:
        debug("Unable to connect")
        error[0] = True
        with cv:
            cv.notify_all()


def capture():
    debug(f"Connecting to {HOST}")

    cv = threading.Condition()
    stream_capture = BytesIO()
    stream_image = BytesIO()
    images = []
    error = [False]

    if not THREADS:
        try:
            ws = create_connection(STREAM_URL)
            threading.Thread(target=read, args=(ws,)).start()
        except:
            debug("Unable to connect")
            return

    for _ in range(THREADS):
        threading.Thread(target=sender, args=(images, cv, error)).start()

    with picamera.PiCamera() as camera:
        camera.resolution = RESOLUTION
        camera.vflip = VFLIP
        camera.hflip = HFLIP

        for _ in camera.capture_continuous(stream_capture, 'jpeg', use_video_port=True):
            time.sleep(DELAY)
            debug("Capture")
            debug("Active threads:", threading.active_count())
            stream_capture.seek(0)
            stream_image.seek(0)
            stream_image.truncate()
            try:
                Image.open(stream_capture).save(stream_image, 'jpeg', optimize=True, quality=QUALITY)
            except:
                pass
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
        time.sleep(TIME_BETWEEN_CONNECTION_RETRIES)


main()
