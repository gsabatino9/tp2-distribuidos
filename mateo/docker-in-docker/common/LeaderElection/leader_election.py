import logging
from common.LeaderElection.middleware import Middleware
from common.LeaderElection.control_sender import ControlSender 
from common.LeaderElection.control_receiver import ControlReceiver
from common.LeaderElection.election_starter import ElectionStarter


class LeaderElection:
    def __init__(self, my_id, n_process, stop_leader_actions_callback):
        self.my_id = my_id
        self.leader_id = None
        self.stop_leader_actions_callback = stop_leader_actions_callback
        self.middleware = Middleware(my_id, n_process)
        self.control_sender = ControlSender(self.middleware)
        self.election_starter = ElectionStarter(self.control_sender)
        self.control_receiver = ControlReceiver(my_id, self.middleware,
                                                self.election_starter, self.control_sender)

    def run(self):
        self.control_sender.start()
        self.election_starter.start()
        self.control_receiver.start()
        logging.info(f"action: init_leader_election | result: success")

