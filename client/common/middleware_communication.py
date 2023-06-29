import random, time, socket, signal
from protocol.communication_client import CommunicationClient

MAX_TIME_POLLING = 4

def connect(addresses, id_client, suscriptions, id_batch=0):
    not_connected = True
    conn = None
    time_to_sleep = 0.25
    max_tries = 10

    while not_connected and max_tries > 0:
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
                f"action: client_connected | result: failures | msg: retrying in {time_to_sleep}sec"
            )
            time.sleep(min(time_to_sleep, MAX_TIME_POLLING))
            time_to_sleep *= 2
        max_tries -= 1
    return conn


def __pick_address(addresses):
    return random.choice(addresses)

