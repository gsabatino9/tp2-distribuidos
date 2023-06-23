import docker
import threading
import logging


class DockerRestarter(threading.Thread):
    def __init__(self, restart_containers_q, create_connections_q):
        super().__init__()
        self.restart_containers_q = restart_containers_q
        self.create_connections_q = create_connections_q
        self.docker_client = docker.from_env()
        self.active = True

    def run(self):
        try:
            self.__execute_docker_restarter_operations()
        except Exception as e:
            logging.error(f"action: docker_restarter_error | error: {str(e)}")
        except:
            logging.error(f"action: docker_restarter_error | error: unknown")

    def __execute_docker_restarter_operations(self):
        while self.active:
            container_name = self.restart_containers_q.get()
            if not container_name:
                if self.active:
                    logging.error(f"action: docker_restarter_error | error: container_is_none")
                continue
            logging.info(f"action: restart_container | container: {container_name}")
            container = self.docker_client.containers.get(container_name)
            container.restart()
            self.create_connections_q.put(container_name)

    def stop(self):
        self.active = False
        self.restart_containers_q.put(None)
