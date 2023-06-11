import docker
import random
import time

MIN_TIME_SLEEP = 1.0
MAX_TIME_SLEEP = 10.0

class DockerStopper:
    def __init__(self, network_name):
        self.network_name = network_name
        self.docker_client = docker.from_env()


    def run(self):
        while True:
            sleep_time = random.uniform(MIN_TIME_SLEEP, MAX_TIME_SLEEP)
            print(f"Por dormir {sleep_time}")
            time.sleep(sleep_time)
            self.docker_client.reload()
            containers = self.__get_containers_in_network()
            container_to_stop = containers[random.randrange(len(containers))]
            print(f"Por stoppear al contenedor {container_to_stop.name}")
            container_to_stop.stop()

    def __get_containers_in_network(self):
        containers = []
        for container in self.docker_client.containers.list():
            networks = container.attrs['NetworkSettings']['Networks']
            if self.network_name in networks:
                containers.append(container)
        return containers