from common.healthy_checker import HealthyChecker
import os
import logging
import docker
import socket


logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level="DEBUG",
    datefmt='%Y-%m-%d %H:%M:%S',
)

docker_logger = logging.getLogger('docker')
docker_logger.setLevel(logging.INFO)

socket_logger = logging.getLogger('socket')
socket_logger.setLevel(logging.INFO)


my_id = int(os.environ.get("ID_ELECTION"))
n_processes = int(os.environ.get("N_PROCESS_ELECTION"))


def main():
    healthy_checker = HealthyChecker("tp1_testing_net", my_id, n_processes)
    healthy_checker.run()


if __name__ == "__main__":
    main()
