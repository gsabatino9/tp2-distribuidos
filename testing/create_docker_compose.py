import sys, json
from init_config import *


def main():
    with open("testing/testing_config.json") as f:
        json_config = json.load(f)

    restarter_config = json_config["config"]["process_restarter"]

    process_restarter = ""
    for i in range(restarter_config["n_processes"]):
        process_restarter += PROCESS_RESTARTER.format(
            i,
            i,
            i,
            restarter_config["n_processes"],
            "",
            restarter_config["network_problems"],
            restarter_config["ip_base"],
            restarter_config["ip_base"][0:-1]
            + str(int(restarter_config["ip_base"].split(".")[-1]) + i),
        )

    processes_to_stop = ""
    for i in range(restarter_config["n_processes"]):
        processes_to_stop += f"processes-restarter-{i},"

    process_stopper = PROCESS_STOPPER.format(processes_to_stop[0:-1])

    compose = (
        INIT_DOCKER.format()
        .replace("<PROCESS_RESTARTER>", process_restarter)
        .replace("<PROCESS_STOPPER>", process_stopper)
    )

    with open("docker-compose-testing-restarters.yaml", "w") as compose_file:
        compose_file.write(compose)


if __name__ == "__main__":
    main()
