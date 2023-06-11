import threading
import queue
import time
import logging
import socket
import signal
from common.utils import ARE_YOU_ALIVE_MESSAGE, HEALTHCHECK_TIMEOUT,\
                         MINIMUM_TIMEOUT_TIME
from common.docker_restarter import DockerRestarter
from common.connection_maker import ConnectionMaker
from common.leader_election.leader_election import LeaderElection
from common.leader_dependent import LeaderDependent
from common.keep_alive.keep_alive import KeepAlive

class HealthyChecker(LeaderDependent):
    def __init__(self, my_id, n_processes, containers_keep_alive, container_restarter_name):
        super().__init__()
        # inaccesible containers.
        self.restart_containers_q = queue.Queue()
        # containers restarted but with no connection 
        self.create_connections_q = queue.Queue()
        # processes with a TCP connection open
        self.connected_processes_q = queue.Queue()

        self.docker_restarter = DockerRestarter(self.restart_containers_q, 
                                                self.create_connections_q,
                                                containers_keep_alive)

        self.connection_maker = ConnectionMaker(self.create_connections_q,
                                                self.connected_processes_q)
        self.leader_election = LeaderElection(my_id, n_processes, 
                                              self.stop_being_leader_callback, 
                                              self.new_leader_callback)
        self.keep_alive = KeepAlive()
        signal.signal(signal.SIGTERM, self.stop)


    def run(self):
        try:
            self.leader_election.run()
            self.keep_alive.start()
            self.connection_maker.start()
            self.docker_restarter.start()
            logging.info("action: healthy_checker_init | result: success")

            while self.active:
                self.wait_until_leader()
                self.__execute_healthcheck_operations()
                self.__free_leader_resources()

            self.connection_maker.join()
            self.docker_restarter.join()
            self.keep_alive.join()
        except Exception as e:
            logging.error(f"action: healthy_checker_error | error: {str(e)}")
        except:
            logging.error(f"action: healthy_checker_error | error: unknown")


    def __execute_healthcheck_operations(self):
        while self.active and self.i_am_leader:
            container, skt, send_time = self.connected_processes_q.get()
            if not container:
                if self.i_am_leader:
                    logging.error(f"action: healthy_checker_error | error: container_is_none")
                continue
            waited_time = time.time() - send_time
            skt.settimeout(max(HEALTHCHECK_TIMEOUT - waited_time, MINIMUM_TIMEOUT_TIME))
            try:
                a = skt.recv(1)
                if not a:
                    raise Exception("No message received")
            except Exception as e:
                logging.error(f"action: healthy_checker_timeout | container: {container}")
                skt.close()
                self.restart_containers_q.put(container)
                continue
            constant_time_loop = max(HEALTHCHECK_TIMEOUT - (time.time() - send_time), 0.0)
            time.sleep(constant_time_loop)
            skt.sendall(ARE_YOU_ALIVE_MESSAGE)
            self.connected_processes_q.put((container, skt, time.time()))

    def stop_being_leader_callback(self):
        logging.debug("Callback de que deje de ser el leader.")
        if self.i_am_leader:
            self.stop_being_leader()
            self.docker_restarter.stop_being_leader()
            self.connection_maker.stop_being_leader()

    def stop_being_leader(self):
        self.i_am_leader = False
        self.connected_processes_q.put((None, None, None))

    def new_leader_callback(self):
        logging.debug("Callback de que empece a ser el leader.")
        self.new_leader_notified()
        self.docker_restarter.new_leader_notified()
        self.connection_maker.new_leader_notified()

    def __free_leader_resources(self):
        try:
            while True:
                container, skt, send_time = self.connected_processes_q.get_nowait()
                if skt:
                    skt.shutdown(socket.SHUT_RDWR)
                    skt.close()
        except queue.Empty:
            # all items in connected_q removed
            pass


    def stop(self, *args):
        self.leader_election.stop()
        # If it's blocked in leader waiting.
        self.stop_waiting()
        # If it's blocked in get container.
        self.stop_being_leader()

        self.docker_restarter.stop()
        self.connection_maker.stop()

        self.keep_alive.stop()