import socket


def suscriptions_to_number(bit_positions):
    byte = 0
    mask = 0

    for bit_position in bit_positions:
        bit_aux = bit_position - 1
        mask |= 1 << bit_aux

    result = byte | mask
    return result


def number_to_suscriptions(number):
    active_bit_positions = []
    bit_position = 0

    while number > 0:
        if number & 1:
            active_bit_positions.append(bit_position + 1)
        bit_position += 1
        number >>= 1

    return active_bit_positions


def close_socket(socket_to_close, resource_str):
    try:
        socket_to_close.shutdown(socket.SHUT_RDWR)
        socket_to_close.close()
    except OSError:
        # if socket was alredy closed:
        print(
            f"action: close_resource | result: success | resource: {resource_str} | msg: socket already closed"
        )
    finally:
        print(f"action: close_resource | result: success | resource: {resource_str}")
