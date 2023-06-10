import socket
CONNECTION_PORT = 12345

ALIVE = b'1'
class KeepAlive:
    def __init__(self):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', CONNECTION_PORT))
        self._server_socket.listen(5)
        self.skt = None

    def run(self):
        print("Por aceptar")
        self.skt, addr = self._server_socket.accept()
        print("se acepta")
        while True:
            print("esperando a recibir del keep alive")
            self.skt.recv(1)
            self.skt.sendall(ALIVE)

    def stop(self):
        if self.skt:
            self.skt.shutdown(socket.SHUT_RDWR)