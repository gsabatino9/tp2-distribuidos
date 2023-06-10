import multiprocessing as mp
import time
from common.utils import ARE_YOU_ALIVE_MESSAGE, HEALTHCHECK_TIMEOUT, MINIMUM_TIMEOUT_TIME
from common.DockerRestarter import DockerRestarter, run_restarter
from common.ConnectionMaker import ConnectionMaker, run_connection_maker


class HealthyChecker:
    def __init__(self, network_name):
        # inaccesible containers.
        self.restart_containers_q = mp.Queue()
        # containers restarted but with no connection 
        self.create_connections_q = mp.Queue()
        # processes with a TCP connection open
        self.connected_processes_q = mp.Queue()

        self.docker_restarter = DockerRestarter(self.restart_containers_q, 
                                                self.create_connections_q,
                                                network_name)

        self.connection_maker = ConnectionMaker(self.create_connections_q,
                                                self.connected_processes_q,
                                                network_name)
        print("todo se crea ok")
        self.p = mp.Process(target=run_connection_maker, args=(self.connection_maker,))
        self.q = mp.Process(target=run_restarter, args=(self.docker_restarter,))
        self.active = True

    def run(self):
        self.p.start()
        self.q.start()
        while self.active:
            container, skt, send_time = self.connected_processes_q.get()
            print(f"Obtengo un contendor para hacer recv: {container}")
            waited_time = time.time() - send_time
            skt.settimeout(max(HEALTHCHECK_TIMEOUT - waited_time, MINIMUM_TIMEOUT_TIME))
            try:
                a = skt.recv(1)
                if not a:
                    raise Exception("No message received")
            except Exception as e:
                print(f"Salta el timeout")
                skt.close()
                self.restart_containers_q.put(container)
                continue
            sleep_for_constant_loop = max(HEALTHCHECK_TIMEOUT - (time.time() - send_time), 0.0)
            time.sleep(sleep_for_constant_loop)
            skt.sendall(ARE_YOU_ALIVE_MESSAGE)

            self.connected_processes_q.put((container, skt, time.time()))

        self.p.join()
        self.q.join()

    def stop(self):
        self.active = False
        self.connected_processes_q.close()
        self.restart_containers_q.put(None)
        self.restart_containers_q.close()
        self.create_connections_q.put(None)
        self.create_connections_q.close(None)
