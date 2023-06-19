from common.results_sender import ResultsSender
import os

HOST = os.environ.get("HOST")
PORT = int(os.environ.get("PORT"))
NAME_RECV_EXCHANGE = "results_exchange"
NAME_RECV_QUEUE = "results_queue"


def main():
    results_sender = ResultsSender(
        HOST, PORT, NAME_RECV_EXCHANGE, NAME_RECV_QUEUE
    )
    results_sender.run()
    results_sender.stop()


if __name__ == "__main__":
    main()
