from src import TCPCameraServer, TCPCameraHandler, FalseCamera, StreamingOutput

class FalseCameraHandler(TCPCameraHandler):
    camera = FalseCamera()
    output = StreamingOutput()
    camera.start_recording(output)

def main():
    host, port = "localhost", 8000

    with TCPCameraServer((host, port), FalseCameraHandler) as server:
        print(f"Serving at {host}, {port}")
        while True:
            server.handle_request()

if __name__ == "__main__":
    main()
