from enum import Enum

# KEEP ALIVE
HEALTHCHECK_TIMEOUT = 0.5
TIME_BETWEEN_HEALTHCHECKS = 1.0
N_RETRIES_CONTACT_LEADER = 2

# SELF PROCLAIMER
SELF_PROCLAIMER_TIMEOUT = 1.0


# MIDDLEWARE
CONNECTION_PORT = 6767

# Si una eleccion no se completa en este tiempo, el contenedor decidira volver a empezarla.
MAX_TIME_WAITING_FOR_ELECTION = 20.0

NO_LEADER = None


class Message(Enum):
    ELECTION = b"E"
    COORDINATOR = b"C"
    ELECTION_ACK = b"A"
    LEADER_ALIVE = b"L"
    LEADER_ALIVE_REPLY = b"R"
