import threading
import queue
from common.leader_election.utils import Message
import logging

class ControlSender(threading.Thread):
    def __init__(self, middleware):
        super().__init__()
        self.middleware = middleware
        self.send_queue = queue.Queue()
        self.active = True

    def run(self):
        try:
            self.__run_loop()
        except Exception as e:
            if not self.active:
                return
            logging.error(f"action: control_sender_error | error: {str(e)}")
        except:
            if not self.active:
                return
            logging.error(f"action: control_sender_error | error: unknown")

    def __run_loop(self):
        while self.active:
            msg, id_to = self.send_queue.get()
            if msg == Message.ELECTION.value:
                self.middleware.broadcast_bigger(msg)
            elif msg == Message.COORDINATOR.value:
                self.middleware.broadcast(msg)
            elif msg in [Message.ELECTION_ACK.value, 
                         Message.LEADER_ALIVE.value, 
                        Message.LEADER_ALIVE_REPLY.value]:
                self.middleware.send(msg, id_to)
            else:
                if self.active:
                    raise Exception(f"Invalid Message Received: {msg}. From: {id_from}")

    def stop(self):
        if not self.active:
            logging.error(f"action: control_sender_error | error: already_stopped")
            return
        self.active = False
        self.send_queue.put((None, None))

    def send_election(self):
        self.send_queue.put((Message.ELECTION.value, None))

    def send_election_ack(self, id_to):
        self.send_queue.put((Message.ELECTION_ACK.value, id_to))
        
    def send_coordinator(self):
        self.send_queue.put((Message.COORDINATOR.value, None))

    def send_alive(self, coordinator_id):
        self.send_queue.put((Message.LEADER_ALIVE.value, coordinator_id))
        
    def send_alive_reply(self, id_to):
        self.send_queue.put((Message.LEADER_ALIVE_REPLY.value, id_to))
