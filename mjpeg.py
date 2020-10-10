import logging
import os
import time
import cv2
import numpy as np

from server import MjpegServer

logging.basicConfig()
log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
logger = logging.getLogger("mjpeg")
log_level = getattr(logging, log_level)
logger.setLevel(log_level)

# dummy camera class for demonstration


class Camera:

    def __init__(self, idx):
        self._idx = idx

    @property
    def identifier(self):
        return self._idx

    # The camera class should contain a "get_frame" method
    def get_frame(self):
        '''
            method to get frames
            It returns the encoded jpeg image
        '''
        frame = np.ones([128, 128, 3], dtype=np.uint8) + \
            np.random.randint(0, 255)
        frame = cv2.imencode('.jpg', frame)[1]
        time.sleep(1 / 25)
        return frame.tobytes()

    def stop(self):
        pass


if __name__ == "__main__":

    # Instantiate Server
    server = MjpegServer()

    # create lookup of routes and different camera objects
    cams = {"cam1": Camera(0),
            "cam2": Camera(1),
            "cam3": Camera(2)
            }

    for route, cam in cams.items():
        # add routes
        server.add_route(route, cam)

    try:
        # start server
        server.start()

    except KeyboardInterrupt:
        logger.warning("Keyboard Interrupt, exiting...")
    finally:
        server.stop()
        for cam in cams.values():
            cam.stop()
