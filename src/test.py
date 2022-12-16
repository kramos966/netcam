import socketserver
import io
import logging
import time
import numpy as np
import PIL
import PIL.Image
from threading import Condition, Thread, Event
from http import server

PAGE = """\
<html>
    <head>
        <title>TEST DE WEV SERVER</title>
    </head>
    <body>
        <h1>I should see a stream of images down below</h1>
        <button type="button" onclick="alert('Su, su, ara mateix...')">Capture!</button>
        <img src="stream.mjpg" width="640" height="480" />
    </body>
</html>"""

class FalseCamera:
    def __init__(self, w=640, h=480):
        self.w, self.h = self.size = w, h

    def capture(self, buf, format):
        while True:
            array = np.uint8(np.random.rand(self.h, self.w, 3)*256)
            im_pil = PIL.Image.fromarray(array)
            im_pil.save(buf, format=format)

            if self.event.is_set():
                break

    def start_recording(self, buf, format="jpeg"):
        self.t = Thread(target=self.capture, args=(buf, format))
        self.event = Event()
        self.t.start()

    def close(self):
        if self.t:
            self.event.set()
            self.t.join()

class StreamingOutput:
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # Ha començat un nou frame
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    """Classe per a processar les requests fetes al servidor
    per cadascun dels clients que hi hagi connectats..."""
    
    # Camera init
    output = StreamingOutput()
    camera = FalseCamera()
    camera.start_recording(output)

    def do_GET(self):
        """Aquest mètode determina què ha d'enviar el servidor un cop
        el client faci una demanda d'informació. Només es tindran en 
        compte els casos contemplats dins d'aquesta funció."""
        # Es demana la localització del fitxer
        if self.path == "/":
            self.send_response(301)
            self.send_header("Location", "/index.html")
            self.end_headers()
        # Què retornem si ens demanen per l'arxiu index.html
        elif self.path == "/index.html":
            content = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)
        # Què retornem en ser demanats per l'arxiu stream.mjpg
        elif self.path == "/stream.mjpg":
            self.send_response(200)
            self.send_header("Age", 0)
            self.send_header("Cache-Control", "no-cache, private")
            self.send_header("Pragma", "no-cache")
            self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=FRAME")
            self.end_headers()

            # Enviem un seguit d'imatges fins que la connexió es perdi
            try:
                while True:
                    with self.output.condition:
                        self.output.condition.wait()
                        frame = self.output.frame
                    self.wfile.write(b"--FRAME\r\n")
                    self.send_header("Content-Type", "image/jpeg")
                    self.send_header("Conent-Length", len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(f"Removed streaming client {self.client_address}: {str(e)}")
        else:
            self.send_error(404)
            self.end_headers()

    def camera_close(self):
        self.camera.close()

class StreamingServer(server.ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def camera_close(self):
        self.server.camera_close()

def main():
    address = ("", 8000)
    server = StreamingServer(address, StreamingHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down server")
    server.server_close()
    server.camera_close()

if __name__ == "__main__":
    main()

