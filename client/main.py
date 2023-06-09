from common.client import Client
import os, ast

HOST = os.environ.get("HOST")
PORT = int(os.environ.get("PORT"))
ADDR_CONSULT = (os.environ.get("HOST_CONSULT"), int(os.environ.get("PORT_CONSULT")))
CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE"))
MAX_RETRIES = int(os.environ.get("MAX_RETRIES"))
SUSCRIPTIONS = os.environ.get("SUSCRIPTIONS")


def main():
    suscriptions = ast.literal_eval(SUSCRIPTIONS)
    client = Client(HOST, PORT, CHUNK_SIZE, MAX_RETRIES, suscriptions)

    filepath = "data/"
    types_files = ["stations", "weather", "trips"]
    client.run(filepath, types_files, ADDR_CONSULT)
    client.stop()


if __name__ == "__main__":
    main()
