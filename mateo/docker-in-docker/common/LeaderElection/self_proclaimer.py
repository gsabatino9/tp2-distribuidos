import threading
import logging

SELF_PROCLAIMER_TIMEOUT = 1

class SelfProclaimer:
    def __init__(self, control_sender):
        self.control_sender = control_sender
        self.timer = None

    def start(self):
        logging.info("action: self_proclaimer | result: started")
        self.timer = threading.Timer(SELF_PROCLAIMER_TIMEOUT, self.__proclaim_leader)
        self.timer.start()

    def stop(self):
        if self.timer:
            self.timer.cancel()
            self.timer = None
            logging.info("action: self_proclaimer | result: canceled")

    def __proclaim_leader(self):
        logging.info("action: self_proclaimer | result: coordintor_called")
        self.control_sender.send_coordinator()

