BUF_SIZE = int(2**16)

PROTOCOL_OK = b'\xbe'

CAM_RECV = b'\x01'
CAM_STOP = b'\xff'
CAM_ERROR = b'\xbf'

SIZEOF_uint32 = 32

class MsgProtocol:
    def __init__(self):
        pass

    def send_bytes(self, sock, byteobj):
        # First, we need to send the size of the message
        length = len(byteobj)
        sock.sendall(length.to_bytes(SIZEOF_uint32, "little"))

        # Get the OK from the other part
        if (not self.wait_ok(sock)):
            raise OSError

        # Send the object, per se
        sock.sendall(byteobj)

        # Receive OK
        if (not self.wait_ok(sock)):
            raise OSError

    def receive_bytes(self, sock):
        # Receive the length of the message
        msg = sock.recv(BUF_SIZE)
        length = int.from_bytes(msg, "little")

        # Send OK
        self.send_ok(sock)

        # Receive the message per se
        msg = b''
        while len(msg) < length:
            packet = sock.recv(BUF_SIZE)
            msg += packet
        # Send OK
        self.send_ok(sock)
        
        return msg

    def send_ok(self, sock):
        sock.sendall(PROTOCOL_OK)

    def wait_ok(self, sock):
        msg = b''
        while len(msg) < 1:
            packet = sock.recv(BUF_SIZE)
            msg += packet
        return msg == PROTOCOL_OK
