from common.session_manager import SessionManager
import os

MAX_CLIENTS = int(os.environ.get("MAX_CLIENTS"))
NAME_RECV_QUEUE = os.environ.get("NAME_RECV_QUEUE")
NAME_SEND_QUEUE = os.environ.get("NAME_SEND_QUEUE")
NAME_END_SESSION_QUEUE = os.environ.get("NAME_END_SESSION_QUEUE")


def main():
    session_manager = SessionManager(
        MAX_CLIENTS, NAME_RECV_QUEUE, NAME_SEND_QUEUE, NAME_END_SESSION_QUEUE
    )
    session_manager.run()
    session_manager.stop()


if __name__ == "__main__":
    main()
