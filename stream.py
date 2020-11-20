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
import logging
import os


# Default settings
RESOLUTION = (640, 480)
IP = 'makentnu.no'
PORT = 80
KEY = 'SECRET'
STREAM_NAME = 'STREAM'
DEBUG = True
VFLIP = False
HFLIP = False
THREADS = 3
DELAY = 0
QUALITY = 50
LOG_FOLDER = "logs"
LOG_FILENAME= os.path.join(LOG_FOLDER, f'{datetime.utcnow().strftime("%Y%m%d-%H%M%S")}_stream_log.log')
LOG_FORMAT = '%(asctime)s %(message)s'
LOG_LEVEL = "ERROR"

# Override defaults with local_settings
try:
    from local_settings import *
except ImportError:
    pass

os.makedirs(LOG_FOLDER, exist_ok=True)
logging.basicConfig(filename=LOG_FILENAME,
                    format=LOG_FORMAT, 
                    filemode='w') 
logger=logging.getLogger(__name__) 

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
    logger.debug(f'Line 64: Send from {threading.current_thread().name}')
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
    except Exception as e:
        logger.error(f'Line 80: {e}')
        error[0] = True
        with cv:
            cv.notify_all()


def capture():
    logger.debug('Connecting to %s on port %s' % (IP, PORT))

    cv = threading.Condition()
    stream_capture = BytesIO()
    stream_image = BytesIO()
    images = []
    error = [False]

    if not THREADS:
        try:
            ws = create_connection('wss://%s/ws/stream/%s/' % (IP, STREAM_NAME))
            threading.Thread(target=read, args=(ws,)).start()
        except Exception as e:
            logger.error(f'Line 100: {e}')
            return

    for _ in range(THREADS):
        threading.Thread(target=sender, args=(images, cv, error)).start()

    with picamera.PiCamera() as camera:
        camera.resolution = RESOLUTION
        camera.vflip = VFLIP
        camera.hflip = HFLIP

        for _ in camera.capture_continuous(stream_capture, 'jpeg', use_video_port=True):
            time.sleep(DELAY)
            logger.debug('Capture')
            logger.debug('Active threads:', threading.active_count())
            stream_capture.seek(0)
            stream_image.seek(0)
            stream_image.truncate()
            try:
                Image.open(stream_capture).save(stream_image, 'jpeg', optimize=True, quality=QUALITY)
            except Exception as e:
                logger.error(f'Line 121: {e}')
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
                except Exception as e:
                    logger.error(e)
                    return
            stream_capture.seek(0)
            stream_capture.truncate()


def main():
    logger.info("Line 140: Initialising")
    while True:
        capture()
        time.sleep(3)


main()
