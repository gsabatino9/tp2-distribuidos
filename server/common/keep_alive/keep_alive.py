import socket
import logging
import threading

CONNECTION_PORT = 12345

ALIVE = b'1'

class KeepAlive(threading.Thread):
    def __init__(self):
        super().__init__()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', CONNECTION_PORT))
        self.server_socket.listen(5)
        self.skt = None
        self.active = True

    def run(self):
        try:
            while self.active:
                logging.debug("action: keep_alive_accept | result: in_progress")
                self.skt, addr = self.server_socket.accept()
                logging.debug("action: keep_alive_accept | result: success")
                self.__run_keep_alive_loop()
        except Exception as e:
            if self.active:
                logging.error(f"action: keep_alive_error | error: {str(e)}")
        except:
            if self.active:
                logging.error(f"action: keep_alive_error | error: unknown")

    def __run_keep_alive_loop(self):
        try:
            while self.active:
                self.skt.recv(1)
                self.skt.sendall(ALIVE)
        except socket.error as e:
            logging.error(f"action: keep_alive_error | error: {str(e)}")
        finally:
            self.skt.close()
            self.skt = None

    def stop(self):
        self.active = False
        if self.skt:
            self.skt.shutdown(socket.SHUT_RDWR)
