from src import TCPCameraServer, TCPCameraHandler

def main():
    host, port = "localhost", 8000

    with TCPCameraServer((host, port), TCPCameraHandler) as server:
        server.timeout = None
        print(f"Serving at {host}, {port}")
        server.serve_forever()

if __name__ == "__main__":
    main()
