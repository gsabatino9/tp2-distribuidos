from common.client import Client
import os

HOST = os.environ.get("HOST")
PORT = int(os.environ.get("PORT"))
ADDR_CONSULT = (os.environ.get("HOST_CONSULT"), int(os.environ.get("PORT_CONSULT")))
CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE"))
MAX_RETRIES = int(os.environ.get("MAX_RETRIES"))
AMOUNT_QUERIES = int(os.environ.get("AMOUNT_QUERIES"))


def main():
    client = Client(HOST, PORT, CHUNK_SIZE, MAX_RETRIES, AMOUNT_QUERIES)

    filepaths = ["data/montreal/", "data/toronto/", "data/washington/"]
    types_files = ["stations", "weather", "trips"]
    cities = ["montreal", "toronto", "washington"]
    client.run(filepaths, types_files, cities, ADDR_CONSULT)
    client.stop()


if __name__ == "__main__":
    main()
