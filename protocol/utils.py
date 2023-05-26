import logging
import socket


def close_socket(socket_to_close, resource_str):
    logging.debug(
        f"action: close_resource | result: in_progress | resource: {resource_str}"
    )
    try:
        socket_to_close.shutdown(socket.SHUT_RDWR)
        socket_to_close.close()
    except OSError:
        # if socket was alredy closed:
        logging.debug(
            f"action: close_resource | result: success | resource: {resource_str} | msg: socket already closed"
        )
    finally:
        logging.info(
            f"action: close_resource | result: success | resource: {resource_str}"
        )
