import time
import socket
import threading
import logging
from common.utils import ARE_YOU_ALIVE_MESSAGE, CONNECTION_PORT,\
                         INIT_TIME_SLEEP, MAX_TIME_SLEEP

class ConnectionMaker(threading.Thread):
    def __init__(self, create_connections_q, connected_processes_q, restart_containers_q):
        super().__init__()
        self.create_connections_q = create_connections_q
        self.connected_processes_q = connected_processes_q
        self.restart_containers_q = restart_containers_q
        self.active = True

    def run(self):
        try:
            self.__execute_create_connections_operations()
        except Exception as e:
            logging.error(f"action: connection_maker_error | error: {str(e)}")
        except:
            logging.error(f"action: connection_maker_error | error: unknown")


    def __execute_create_connections_operations(self):
        while self.active:
            container_name = self.create_connections_q.get()
            if not container_name:
                if self.active:
                    logging.error(f"action: connection_maker_error | error: container_is_none")
                continue
            self.__create_connection(container_name)


    def __create_connection(self, container_addr):
        sleep_time = INIT_TIME_SLEEP
        while self.active:
            try:
                # avoid busy waiting. Restart 
                time.sleep(sleep_time)
                skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                skt.connect((container_addr, CONNECTION_PORT))
                skt.sendall(ARE_YOU_ALIVE_MESSAGE)
                self.connected_processes_q.put((container_addr, skt, time.time()))
                return
            except Exception as e:
                logging.error(f"Error: {str(e)} | container: {container_addr}")
                # Always try again until max time is waited.
                if sleep_time == MAX_TIME_SLEEP:
                    logging.error(f"ERRORRRR | container: {container_addr}")
                    self.restart_containers_q.put(container_addr)
                    return
                sleep_time = min(sleep_time * 2, MAX_TIME_SLEEP)
                pass


    def stop(self):
        self.active = False
        self.create_connections_q.put(None)
