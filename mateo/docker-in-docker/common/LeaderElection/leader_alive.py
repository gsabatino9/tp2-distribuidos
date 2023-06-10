import threading
import queue
from enum import Enum
import logging
from common.LeaderElection.utils import Message

class LeaderAliveState(Enum):
    LEADER = 1
    FOLLOWER = 2
    WAITING_ELECTION = 3


class LeaderAlive(threading.Thread):
    def __init__(self, my_id, control_sender):
        super().__init__()
        self.my_id = my_id
        self.leader_alive_q = queue.Queue()
        self.state = LeaderAliveState.WAITING_ELECTION
        self.active = True
        self.leader = None

    def run(self):
        while self.active:
            if self.state == LeaderAliveState.LEADER:
                self.__execute_leader()
            elif self.state == LeaderAliveState.FOLLOWER:
                self.__execute_follower()
            elif self.state == LeaderAliveState.WAITING_ELECTION:
                self.__execute_waiting_election()
            else:
                logging.error("error: invalid_leader_alive_state")
                return


    def __execute_leader(self):
        msg, id_from = self.leader_alive_q.get()
        if msg == Message.LEADER_ALIVE:
            self.control_sender

    def coordinator_received(self, id_from):
        self.leader_alive_q.put((Message.COORDINATOR, id_from))

    def start_election(self):
        self.leader_alive_q.put((Message.ELECTION, None))

    def is_leader_alive_received(self, id_from):
        self.leader_alive_q.put((Message.LEADER_ALIVE, id_from))

    def leader_alive_reply_received(self, leader_id):
        self.leader_alive_q.put((Message.LEADER_ALIVE_REPLY, leader_id))
