from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput
import time
import io
from src import TCPCameraServer, TCPCameraHandler, StreamingOutput

class PiCameraHandler(TCPCameraHandler):
    output = StreamingOutput()
    camera = Picamera2()
    preview_config = camera.create_video_configuration(main={"size":(640, 480)})
    still_config = camera.create_still_configuration(main={"size":(4056, 3040)})
    camera.configure(preview_config)

    encoder = MJPEGEncoder()
    # Let the camera stabilize into sensible values of gain
    camera.start_recording(encoder, FileOutput(output))     # Here, the camera starts infinitely recording video into circular buffer
    #camera.exposure_mode = "off"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_shutter_speed(self, shutter_speed):
        #self.camera.shutter_speed = shutter_speed
        pass

    def still_capture(self):
        still_output = io.BytesIO()
        self.camera.stop_recording()
        self.camera.start()
        self.camera.switch_mode_and_capture_file(self.still_config, still_output, format="jpeg")
        self.camera.stop()

        self.camera.start_recording(self.encoder, FileOutput(self.output))
        return still_output.getbuffer()

if __name__ == "__main__":
    host, port = "0.0.0.0", 8000
    with TCPCameraServer((host, port), PiCameraHandler) as server:
        print(f"Serving at {host}, {port}")
        while True:
            server.handle_request()
