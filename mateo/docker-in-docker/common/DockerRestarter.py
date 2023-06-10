import time
import docker

def run_restarter(restarter):
    restarter.run()


class DockerRestarter:
    def __init__(self, restart_containers_q, create_connections_q, network_name):
        self.network_name = network_name
        self.restart_containers_q = restart_containers_q
        self.create_connections_q = create_connections_q
        self.active = True
        self.docker_client = docker.from_env()
        self.__add_containers_in_network()

    def run(self):
        while self.active:
            container_name = self.restart_containers_q.get()
            print(f"Por hacer restart de: {container_name}")
            container = self.docker_client.containers.get(container_name)
            container.restart()
            self.create_connections_q.put(container_name)


    def __add_containers_in_network(self):
        for container in self.docker_client.containers.list():
            networks = container.attrs['NetworkSettings']['Networks']
            if self.network_name in networks:
                self.create_connections_q.put(container.name)

    def stop(self):
        self.active = False
        self.restart_containers_q.close()
        self.create_connections_q.close()
