import logging
from common.leader_election.middleware import Middleware
from common.leader_election.control_sender import ControlSender 
from common.leader_election.control_receiver import ControlReceiver
from common.leader_election.election_starter import ElectionStarter
from common.leader_election.leader_alive import LeaderAlive


class LeaderElection:
    def __init__(self, my_id, n_process, stop_leader_actions_callback, i_am_leader_callback):
        self.my_id = my_id
        self.leader_id = None
        self.middleware = Middleware(my_id, n_process)
        self.control_sender = ControlSender(self.middleware)
        self.election_starter = ElectionStarter(self.control_sender)
        self.leader_alive = LeaderAlive(self.my_id, self.control_sender, self.election_starter)
        self.control_receiver = ControlReceiver(my_id, self.middleware, self.election_starter,
                                                self.control_sender, self.leader_alive, 
                                                stop_leader_actions_callback, i_am_leader_callback)

    def run(self):
        self.control_sender.start()
        self.election_starter.start()
        self.leader_alive.start()
        self.control_receiver.start()

    def stop(self):
        logging.debug(f"action: stop_leader_election_processes | result: in_progress")
        self.control_sender.stop()
        self.election_starter.stop()
        self.leader_alive.stop()
        self.control_receiver.stop()

        self.control_sender.join()
        self.election_starter.join()
        self.leader_alive.join()
        self.control_receiver.join()
        self.middleware.close()
        logging.debug(f"action: stop_leader_election_processes | result: success")
