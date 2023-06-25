import threading
import logging
from common.leader_election.utils import SELF_PROCLAIMER_TIMEOUT


class SelfProclaimer:
    def __init__(self, control_sender):
        self.control_sender = control_sender
        self.timer = None
        self.timer_active = False

    def start(self):
        logging.debug("action: self_proclaimer | result: started")
        self.stop()
        self.timer_active = True
        self.timer = threading.Timer(SELF_PROCLAIMER_TIMEOUT, self.__proclaim_leader)
        self.timer.start()

    def stop(self):
        if self.timer_active:
            self.timer.cancel()
            self.timer_active = False
            self.timer = None
            logging.debug("action: self_proclaimer | result: canceled")

    def __proclaim_leader(self):
        logging.debug("action: self_proclaimer | result: self_proclaim_leader_called")
        self.control_sender.send_coordinator()
