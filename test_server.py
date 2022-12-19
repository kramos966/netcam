from src import TCPCameraServer, TCPCameraHandler

def main():
    host, port = "localhost", 8000

    with TCPCameraServer((host, port), TCPCameraHandler) as server:
        print(f"Serving at {host}, {port}")
        while True:
            server.handle_request()

if __name__ == "__main__":
    main()
