import threading
import queue
from common.LeaderElection.utils import Message
from common.LeaderElection.self_proclaimer import SelfProclaimer
import logging
import time
NO_LEADER = None


class ElectionStarter(threading.Thread):
    def __init__(self, control_sender):
        super().__init__()
        self.leader_id = NO_LEADER
        self.start_election_q = queue.Queue()
        self.active = True
        self.control_sender = control_sender
        self.self_proclaimer = SelfProclaimer(control_sender)

    def run(self):
        time.sleep(1)
        self.__execute_election()
        while self.active:
            msg, id_from = self.start_election_q.get()
            if msg == Message.ELECTION and self.leader_id != NO_LEADER:
                self.__execute_election()
            elif msg == Message.ELECTION_ACK:
                self.self_proclaimer.stop()
            elif msg == Message.COORDINATOR:
                logging.info(f"action: election | result: finished | coordinator: {id_from}")
                self.leader_id = id_from
                self.self_proclaimer.stop()    
    
    def start_election(self):
        self.start_election_q.put((Message.ELECTION, None))

    def coordinator_received(self, id_from):
        self.start_election_q.put((Message.COORDINATOR, id_from))

    def election_ack(self):
        self.start_election_q.put((Message.ELECTION_ACK, None))

    def __execute_election(self):
        self.leader_id = NO_LEADER
        self.control_sender.send_election()
        self.self_proclaimer.start()
        logging.info("action: election | result: started")
