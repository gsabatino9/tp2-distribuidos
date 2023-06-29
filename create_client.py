import sys, json, uuid
from init_config import *


def main(amount_clients):
    clients = ""
    for i in range(1, amount_clients + 1):
        id_client = uuid.uuid4().int >> 64

        clients += CLIENT.format(
            i,
            i,
            id_client,
            i,
        )

    compose = INIT_CLIENT.format().replace("<CLIENT>", clients)

    with open("docker-compose-client.yaml", "w") as compose_file:
        compose_file.write(compose)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Error: Missing amount_clients")
    else:
        try:
            amount_clients = int(sys.argv[1])
            main(amount_clients)
        except ValueError:
            print("Error: amount_clients must be an integer.")
