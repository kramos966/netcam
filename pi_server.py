import picamera
from src import TCPCameraServer, TCPCameraHandler, StreamingOutput

class PiCameraHandler(TCPCameraHandler):
    output = StreamingOutput()
    camera = picamera.PiCamera()
    camera.resolution = 1280, 960
    camera.start_recording(output, format="mjpeg")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


if __name__ == "__main__":
    host, port = "0.0.0.0", 8000
    with TCPCameraServer((host, port), PiCameraHandler) as server:
        print(f"Serving at {host}, {port}")
        while True:
            server.handle_request()