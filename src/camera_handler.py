import socketserver
from .test import FalseCamera, StreamingOutput

from .protocol import MsgProtocol, CAM_RECV, CAM_STOP, CAM_ERROR, TIMEOUT

class TCPCameraHandler(socketserver.BaseRequestHandler, MsgProtocol):
    # Timeout. If no activity is perceived in timeout seconds, raise exception...
    timeout = TIMEOUT    # s

    def setup(self):
        """Setup the request handler so that it's able to access and read
        the stream originating from the camera."""
        self.camera = FalseCamera()
        self.output = StreamingOutput()

        self.camera.start_recording(self.output)


    def handle(self):
        # Read out the whole request
        print(f"Received request from {self.client_address}")
        msg = self.receive_bytes(self.request)
        if msg == CAM_RECV:
            # We are requested an image
            print(f"Sending image stream to {self.client_address}")
            while True:
                with self.output.condition:
                    try:
                        self.output.condition.wait()
                    except TimeoutError:
                        continue
                    frame = self.output.frame
                if len(frame) != 0:
                    # Once the frame is complete, we send it to the client
                    try:
                        self.send_bytes(self.request, frame)
                    except:
                        print(f"Shutting down connexion with {self.client_address}")
                        break

        elif msg == CAM_STOP:
            pass

        print(f"Finished processing request from {self.client_address}")

    def finish(self):
        self.camera.close()

class TCPCameraServer(socketserver.TCPServer):
    """Only serving ONE client at a time!"""
    timeout = TIMEOUT # s, timeout before deeming a connection lost

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(f"Timeout = {self.timeout} s")
