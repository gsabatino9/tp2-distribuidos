from common.client import Client
import os, ast

ADDRESSES = os.environ.get("ADDRESSES")
ADDR_CONSULT = (os.environ.get("HOST_CONSULT"), int(os.environ.get("PORT_CONSULT")))
CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE"))
MAX_RETRIES = int(os.environ.get("MAX_RETRIES"))
SUSCRIPTIONS = os.environ.get("SUSCRIPTIONS")
FILE_PATH = os.environ.get("FILE_PATH")
ID_CLIENT = int(os.environ.get("ID_CLIENT"))


def main():
    suscriptions = ast.literal_eval(SUSCRIPTIONS)
    addresses = ast.literal_eval(ADDRESSES)

    client = Client(addresses, CHUNK_SIZE, MAX_RETRIES, ID_CLIENT, suscriptions)

    types_files = ["stations", "weather", "trips"]
    client.run(FILE_PATH, types_files, ADDR_CONSULT)
    client.stop()


if __name__ == "__main__":
    main()
