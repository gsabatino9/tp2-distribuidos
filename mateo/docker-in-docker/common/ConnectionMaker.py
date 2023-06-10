import time
import socket
import docker
from common.utils import ARE_YOU_ALIVE_MESSAGE


CONNECTION_PORT = 12345
INIT_TIME_SLEEP = 1.0
MAX_TIME_SLEEP = 10.0

def run_connection_maker(connection_maker):
    connection_maker.run()


class ConnectionMaker:
    def __init__(self, create_connections_q, connected_processes_q, network_name):
        self.create_connections_q = create_connections_q
        self.connected_processes_q = connected_processes_q
        self.network_name = network_name
        self.docker_client = docker.from_env()
        self.active = True

    def run(self):
        while self.active:
            container_name = self.create_connections_q.get()
            container = self.docker_client.containers.get(container_name)
            self.__create_connection(container)

    def __create_connection(self, container):
        sleep_time = INIT_TIME_SLEEP
        while True:
            try:
                # avoid busy waiting. Restart 
                time.sleep(sleep_time)
                container.reload()
                ip_addr = container.attrs['NetworkSettings']['Networks'][self.network_name]['IPAddress']
                skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                skt.connect((ip_addr, CONNECTION_PORT))
                skt.sendall(ARE_YOU_ALIVE_MESSAGE)
                self.connected_processes_q.put((container.name, skt, time.time()))
                return
            except Exception as e:
                print(f"Error: {str(e)}")
                # Always try again until max time is waited.
                if sleep_time == MAX_TIME_SLEEP:
                    print("ERRORRRR")
                    return
                sleep_time = min(sleep_time * 2, MAX_TIME_SLEEP)
                pass

    def stop(self):
        self.active = False
        self.create_connections_q.close()
