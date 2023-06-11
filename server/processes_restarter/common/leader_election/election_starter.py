import threading
import queue
from common.leader_election.utils import Message, NO_LEADER
from common.leader_election.self_proclaimer import SelfProclaimer
import logging

class ElectionStarter(threading.Thread):
    def __init__(self, control_sender):
        super().__init__()
        self.leader_id = NO_LEADER
        self.start_election_q = queue.Queue()
        self.control_sender = control_sender
        self.self_proclaimer = SelfProclaimer(control_sender)
        self.active = True

    def run(self):
        try:
            self.__run_loop()
        except Exception as e:
            if not self.active:
                return
            logging.error(f"action: election_starter_error | error: {str(e)}")
        except:
            if not self.active:
                return
            logging.error(f"action: election_starter_error | error: unknown")
        finally:
            self.self_proclaimer.stop()


    def __run_loop(self):
        self.__execute_election()
        while self.active:
            msg, id_from = self.start_election_q.get()
            if msg == Message.ELECTION:
                if self.leader_id != NO_LEADER:
                    self.__execute_election()
            elif msg == Message.ELECTION_ACK:
                self.self_proclaimer.stop()
            elif msg == Message.COORDINATOR:
                self.leader_id = id_from
                self.self_proclaimer.stop()
                logging.info(f"action: leader_election | result: "
                             f"finished | leader: {self.leader_id}")
            else:
                if self.active:
                    raise Exception(f"Invalid Message Received: {msg}. From: {id_from}")

    def stop(self):
        if not self.active:
            logging.error(f"action: election_starter_error | error: already_stopped")
            return
        self.active = False
        self.start_election_q.put((None, None))

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
        logging.info("action: leader_election | result: started")
