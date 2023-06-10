from enum import Enum

class Message(Enum):
    ELECTION = b'E'
    COORDINATOR = b'C'
    ELECTION_ACK = b'A'
    LEADER_ALIVE = b'L'
    LEADER_ALIVE_REPLY = b'R'
