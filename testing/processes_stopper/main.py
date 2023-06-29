import docker
import random
import time
import logging
import os
import signal

MIN_TIME_SLEEP = 20.0
MAX_TIME_SLEEP = 40.0


class DockerStopper:
    def __init__(self, containers_to_stop):
        self.containers_to_stop = containers_to_stop
        self.docker_client = docker.from_env()
        signal.signal(signal.SIGTERM, self.stop)

        self.running = True

    def run(self):
        while self.running:
            sleep_time = random.uniform(MIN_TIME_SLEEP, MAX_TIME_SLEEP)
            time.sleep(sleep_time)
            container_name = random.choice(self.containers_to_stop)
            container = self.docker_client.containers.get(container_name)
            logging.info(f"action: stop_container | container: {container_name}")
            container.stop(timeout=15)

    def stop(self, *args):
        self.running = False

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level="INFO",
    datefmt="%Y-%m-%d %H:%M:%S",
)

docker_logger = logging.getLogger("docker")
docker_logger.setLevel(logging.INFO)

containers_to_stop = os.environ.get("CONTAINERS_TO_STOP")

stopper = DockerStopper(containers_to_stop.split(","))
stopper.run()
