from common.processes_restarter import ProcessesRestarter
import os
import logging
import docker
import socket


logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level="INFO",
    datefmt='%Y-%m-%d %H:%M:%S',
)

docker_logger = logging.getLogger('docker')
docker_logger.setLevel(logging.INFO)

socket_logger = logging.getLogger('socket')
socket_logger.setLevel(logging.INFO)


my_id = int(os.environ.get("ID_ELECTION"))
n_processes = int(os.environ.get("N_PROCESS_ELECTION"))
containers_keep_alive = os.environ.get("CONTAINERS_KEEP_ALIVE")
container_restarter_name = os.environ.get("CONTAINER_RESTARTER_NAME")

def main():
    processes_restarter = ProcessesRestarter(my_id, n_processes,
                                             containers_keep_alive.split(","),
                                             container_restarter_name)
    processes_restarter.run()


if __name__ == "__main__":
    main()
