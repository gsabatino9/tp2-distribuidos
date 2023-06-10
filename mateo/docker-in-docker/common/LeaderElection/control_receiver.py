from common.LeaderElection.utils import Message
import threading
import logging

class ControlReceiver(threading.Thread):
    def __init__(self, my_id, middleware, election_starter, control_sender):
        super().__init__()
        self.middleware = middleware
        self.my_id = my_id
        self.election_starter = election_starter
        self.control_sender = control_sender
        self.active = True

    def run(self):
        while (self.active):
            logging.info(f"por bloquearme en el recv_message")
            msg, id_from = self.middleware.recv_message()
            if msg == Message.ELECTION.value:
                self.__handle_election(id_from)
            elif msg == Message.COORDINATOR.value:
                self.__handle_coordinator(id_from)
            elif msg == Message.ELECTION_ACK.value:
                self.__handle_election_ack(id_from)
            elif msg == Message.LEADER_ALIVE.value:
                self.__handle_leader_alive(id_from)


    def __handle_election(self, id_from):
        if id_from < self.my_id:
            self.control_sender.send_election_ack(id_from)
        self.election_starter.start_election()

    def __handle_coordinator(self, id_from):
        self.election_starter.coordinator_received(id_from)

    def __handle_election_ack(self, id_from):
        self.election_starter.election_ack()



#    def __handle_leader_alive(self, id_from):
