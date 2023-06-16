from common.results_verifier import ResultsVerifier
import os

HOST = os.environ.get("HOST")
PORT = int(os.environ.get("PORT"))
NAME_RECV_QUEUE = os.environ.get("NAME_RECV_QUEUE")
NAME_EM_QUEUE = os.environ.get("NAME_EM_QUEUE")
AMOUNT_QUERIES = int(os.environ.get("AMOUNT_QUERIES"))


def main():
    results_verifier = ResultsVerifier(NAME_RECV_QUEUE, NAME_EM_QUEUE, HOST, PORT, AMOUNT_QUERIES)
    results_verifier.run()
    results_verifier.stop()


if __name__ == "__main__":
    main()
