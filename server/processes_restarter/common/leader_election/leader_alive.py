import threading
import queue
from enum import Enum
import logging
from common.leader_election.utils import Message, HEALTHCHECK_TIMEOUT,\
                                         N_RETRIES_CONTACT_LEADER,\
                                         TIME_BETWEEN_HEALTHCHECKS, NO_LEADER
                                        
import time

class LeaderAliveState(Enum):
    LEADER = 1
    FOLLOWER = 2
    WAITING_ELECTION = 3

class LeaderAlive(threading.Thread):
    def __init__(self, my_id, control_sender, election_starter):
        super().__init__()
        self.my_id = my_id
        self.control_sender = control_sender
        self.election_starter = election_starter
        self.leader_alive_q = queue.Queue()
        self.state = LeaderAliveState.WAITING_ELECTION
        self.leader = NO_LEADER
        self.active = True
        # Try healthcheck N_RETRIES_CONTACT_LEADER times.
        # If leader doesn't respond, then start ELECTION.
        self.follower_retries = N_RETRIES_CONTACT_LEADER


    def run(self):
        try:
            self.__run_loop()
        except Exception as e:
            if not self.active:
                return
            logging.error(f"action: leader_alive_error | error: {str(e)}")
        except:
            if not self.active:
                return
            logging.error(f"action: leader_alive_error | error: unknown")

    def __run_loop(self):
        while self.active:
            if self.state == LeaderAliveState.LEADER:
                self.__execute_leader()
            elif self.state == LeaderAliveState.FOLLOWER:
                self.__execute_follower()
            elif self.state == LeaderAliveState.WAITING_ELECTION:
                self.__execute_waiting_election()
            else:
                raise Exception("Invalid Leader Alive State")

    def stop(self):
        self.active = False
        self.leader_alive_q.put((None, None))

    def __execute_leader(self):
        msg, id_from = self.leader_alive_q.get()
        if msg == Message.LEADER_ALIVE:
            self.control_sender.send_alive_reply(id_from)
        elif msg == Message.COORDINATOR:
            self.leader = id_from
            if self.leader != self.my_id:
               self.state = LeaderAliveState.FOLLOWER
               self.follower_retries = N_RETRIES_CONTACT_LEADER

    def __execute_follower(self):
        self.control_sender.send_alive(self.leader)
        try:
            self.__wait_for_alive_reply()
        except queue.Empty:
            self.follower_retries = self.follower_retries - 1
            if self.follower_retries > 0:
                return
            logging.debug(f"action: timeout_leader_alive_healthcheck")
            self.election_starter.start_election(self.my_id)
            self.leader = NO_LEADER
            self.state = LeaderAliveState.WAITING_ELECTION

    def __wait_for_alive_reply(self):
        time_sent = time.time()
        timeout_time = HEALTHCHECK_TIMEOUT
        while (timeout_time > 0 and self.active):
            msg, id_from = self.leader_alive_q.get(timeout=timeout_time)
            now = time.time()
            if msg == Message.COORDINATOR:
                self.leader = id_from
                if self.leader == self.my_id:
                    self.state = LeaderAliveState.LEADER
                return
            elif msg == Message.LEADER_ALIVE_REPLY and id_from == self.leader:
                # avoid flooding the network.
                time.sleep(TIME_BETWEEN_HEALTHCHECKS)
                return
            timeout_time = HEALTHCHECK_TIMEOUT - (now - time_sent)
        if self.active:
            # timeout reached -> leader is not responding.
            raise queue.Empty("Timeout reached")

    def __execute_waiting_election(self):
        msg, id_from = self.leader_alive_q.get()
        if msg == Message.COORDINATOR:
            self.leader = id_from
            if self.leader == self.my_id:
                self.state = LeaderAliveState.LEADER
            else:
                self.state = LeaderAliveState.FOLLOWER
                self.follower_retries = N_RETRIES_CONTACT_LEADER

    def coordinator_received(self, id_from):
        self.leader_alive_q.put((Message.COORDINATOR, id_from))

    def leader_alive_received(self, id_from):
        self.leader_alive_q.put((Message.LEADER_ALIVE, id_from))

    def leader_alive_reply_received(self, leader_id):
        self.leader_alive_q.put((Message.LEADER_ALIVE_REPLY, leader_id))
