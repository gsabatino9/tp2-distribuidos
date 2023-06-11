import time
import docker
import queue
import threading
import logging
from common.leader_dependent import LeaderDependent


class DockerRestarter(threading.Thread, LeaderDependent):
    def __init__(self, restart_containers_q, create_connections_q, network_name):
        threading.Thread.__init__(self)
        LeaderDependent.__init__(self)
        self.network_name = network_name
        self.restart_containers_q = restart_containers_q
        self.create_connections_q = create_connections_q
        self.docker_client = docker.from_env()
        self.containers_in_network = []
        self.__add_containers_in_network()

    def run(self):
        try:
            while self.active:
                self.wait_until_leader()
                self.__execute_docker_restarter_operations()
                self.__free_leader_resources()
        except Exception as e:
            logging.error(f"action: docker_restarter_error | error: {str(e)}")
        except:
            logging.error(f"action: docker_restarter_error | error: unknown")

    def __execute_docker_restarter_operations(self):
        if self.active and self.i_am_leader:
            self.__put_containers_create_connections()
        while self.active and self.i_am_leader:
            container_name = self.restart_containers_q.get()
            if not container_name:
                if self.i_am_leader:
                    logging.error(f"action: docker_restarter_error | error: container_is_none")
                continue
            logging.info(f"action: restart_container | container: {container_name}")
            container = self.docker_client.containers.get(container_name)
            container.restart()
            self.create_connections_q.put(container_name)


    def __free_leader_resources(self):
        try:
            while True:
                container_name = self.restart_containers_q.get_nowait()
        except queue.Empty:
            # all items in restart_containers_q removed (i am no longer leader)
            pass


    def stop_being_leader(self):
        self.i_am_leader = False
        self.restart_containers_q.put(None)


    def __add_containers_in_network(self):
        for container in self.docker_client.containers.list():
            networks = container.attrs['NetworkSettings']['Networks']
            if self.network_name in networks:
                self.containers_in_network.append(container.name)


    def __put_containers_create_connections(self):
        for container_name in self.containers_in_network:
            self.create_connections_q.put(container_name)


    def stop(self):
        # If it's blocked in leader waiting.
        self.stop_waiting()
        # If it's blocked in get container.
        self.stop_being_leader()
