import threading
import queue
from common.LeaderElection.utils import Message
import logging



class ControlSender(threading.Thread):
    def __init__(self, middleware):
        super().__init__()
        self.middleware = middleware
        self.send_queue = queue.Queue()
        self.active = True


    def run(self):
        while self.active:
            msg, id_to = self.send_queue.get()
            if msg == Message.ELECTION.value:
                self.middleware.broadcast_bigger(msg)
            elif msg == Message.COORDINATOR.value:
                self.middleware.broadcast(msg)
            elif msg == Message.ELECTION_ACK.value:
                self.middleware.send(msg, id_to)
            elif msg == Message.LEADER_ALIVE.value:
                self.middleware.send(msg, id_to)

    def send_election(self):
        self.send_queue.put((Message.ELECTION.value, None))

    def send_election_ack(self, id_to):
        self.send_queue.put((Message.ELECTION_ACK.value, id_to))
        
    def send_coordinator(self):
        self.send_queue.put((Message.COORDINATOR.value, None))

    def send_alive(self, coordinator_id):
        self.send_queue.put((Message.LEADER_ALIVE.value, coordinator_id))
        
    def send_alive_reply(self, id_to):
        return