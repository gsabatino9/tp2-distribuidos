import random, time, socket, signal
from protocol.communication_client import CommunicationClient


def connect(addresses, id_client, suscriptions, id_batch=0):
    not_connected = True
    conn = None

    while not_connected:
        try:
            address = __pick_address(addresses)
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(address)
            conn = CommunicationClient(client_socket, id_client, suscriptions, id_batch)

            print(
                f"action: client_connected | result: success | addr: {conn.getpeername()} | suscriptions: {suscriptions} | id_batch: {id_batch}"
            )

            not_connected = False
        except:
            print(
                f"action: client_connected | result: failures | msg: retrying in 1sec"
            )
            time.sleep(1)

    return conn


def __pick_address(addresses):
    return random.choice(addresses)
