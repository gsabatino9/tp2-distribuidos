import time
from common.HealthyChecker import HealthyChecker
from common.LeaderElection.leader_election import LeaderElection
import os
import logging


logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level="DEBUG",
    datefmt='%Y-%m-%d %H:%M:%S',
)

my_id = int(os.environ.get("ID_ELECTION"))
n_process = int(os.environ.get("N_PROCESS_ELECTION"))

def __callback():
    logging.info("Se llama al callback para avisar que no soy mas leader")

def main():
    # healthy_checker = HealthyChecker("tp1_testing_net")
    # healthy_checker.run()
    leader_election = LeaderElection(my_id, n_process, __callback)
    leader_election.run()


if __name__ == "__main__":
    main()
