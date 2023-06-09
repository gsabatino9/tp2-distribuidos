from collections import namedtuple
from struct import pack, unpack, calcsize


PACK_CODE = "!I"
Message = namedtuple("Message", "id_client")


def id_client_msg(id_client):
    msg = Message(id_client)
    return pack(PACK_CODE, *msg)


def get_id_client_from_msg(msg):
    return unpack(PACK_CODE, msg)[0]
