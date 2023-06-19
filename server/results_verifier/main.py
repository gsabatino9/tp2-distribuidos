from common.results_verifier import ResultsVerifier
import os

NAME_RECV_QUEUE = os.environ.get("NAME_RECV_QUEUE")
NAME_EM_QUEUE = os.environ.get("NAME_EM_QUEUE")
NAME_RESULTS_EXCHANGE = "results_exchange"
NAME_RESULTS_QUEUE = "results_queue"
AMOUNT_QUERIES = int(os.environ.get("AMOUNT_QUERIES"))


def main():
    results_verifier = ResultsVerifier(
        NAME_RECV_QUEUE,
        NAME_EM_QUEUE,
        NAME_RESULTS_EXCHANGE,
        NAME_RESULTS_QUEUE,
        AMOUNT_QUERIES,
    )
    results_verifier.run()
    results_verifier.stop()


if __name__ == "__main__":
    main()
