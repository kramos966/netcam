import threading
import socket
import io

from .protocol import MsgProtocol, BUF_SIZE, CAM_RECV, TIMEOUT, CAM_SET_OPTIONS, CAM_STILL_CAPTURE

class CameraWatcher(MsgProtocol):
    def __init__(self, n_cameras):
        self.conditions = [threading.Condition() for i in range(n_cameras)]

        self.images = [io.BytesIO() for i in range(n_cameras)]

        self.stop_event = threading.Event()

        self.cameras = {}

    def watch_camera(self, server, ExposureTime=None):
        n_cam = len(self.cameras)   # Creating a new camera
        self.server = server
        self.ExposureTime = ExposureTime
        t = threading.Thread(target=self._watch_camera, args=(server,), kwargs={"ExposureTime":ExposureTime})
        self.cameras[n_cam] = t
        t.daemon = True
        t.start()

    def get_image(self, n_cam, timeout=None):
        with self.conditions[n_cam]:
            self.conditions[n_cam].wait(timeout=timeout)
            frame = self.images[n_cam]

        return frame

    def get_still_image(self, n_cam, timeout=None):
        # We momentarily stop the continuous capture to get a still, hq image
        self.stop_event.set()
        t = self.cameras[n_cam]
        t.join()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(TIMEOUT)
            sock.connect(self.server)

            self.send_bytes(sock, CAM_STILL_CAPTURE)

            # Receive the whole frame
            frame = self.receive_bytes(sock)

        self.stop_event.clear()
        # Once done, restart the continuous capture
        t = threading.Thread(target=self._watch_camera, args=(self.server,), kwargs={"ExposureTime":self.ExposureTime})
        self.cameras[n_cam] = t
        t.daemon = True
        t.start()
        return frame

    def __set_options(self, server, **options):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(TIMEOUT)
            sock.connect(server)
            
            # Commence server communication, asking for speed change
            self.send_bytes(sock, CAM_SET_OPTIONS)
            self.send_json(sock, options)

    def _watch_camera(self, server, **options):
        n_cam = len(self.cameras) - 1

        if options:
            self.__set_options(server, **options)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(TIMEOUT)
            sock.connect(server)
            
            # Commence server communication, asking for camera capture
            self.send_bytes(sock, CAM_RECV)
            while True:
                if self.stop_event.is_set():
                    break
            
                # Poll images
                image = self.receive_bytes(sock)
                # Convert to a BytesIO so that pygame can read them...
                with self.conditions[n_cam]:
                    self.images[n_cam] = io.BytesIO(image)
                    self.conditions[n_cam].notify_all()

    def get_connected_cameras(self):
        return len(self.cameras)

    def close(self):
        # Close all pending connections and sockets
        self.stop_event.set()
        for camera in self.cameras:
            # Kill all children
            t = self.cameras[camera]
            t.join()

    def __del__(self):
        self.close()
