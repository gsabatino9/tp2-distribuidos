import queue
import logging
import signal
from common.docker_restarter import DockerRestarter
from common.connection_maker import ConnectionMaker
from common.healthy_checker import HealthyChecker
from common.leader_election.leader_election import LeaderElection
from common.keep_alive.keep_alive import KeepAlive

NO_LEADER = 0
LEADER = 1
STOP_LEADER_QUEUE = 2
KEEP_ALIVE_ACCEPTED = 3

class ProcessesRestarter:
    def __init__(self, my_id, n_processes, containers_keep_alive, container_restarter_name):
        my_container_name = container_restarter_name + str(my_id)
        restarters_names = [container_restarter_name + str(restarter_id) 
                            for restarter_id in range(n_processes)]
        self.containers_keep_alive = restarters_names[::-1] + containers_keep_alive
        self.containers_keep_alive.remove(my_container_name)
        self.container_restarter_name = container_restarter_name
        self.new_leader_queue = queue.Queue()
        self.leader_election = LeaderElection(my_id, n_processes, 
                                              self.stop_being_leader_callback, 
                                              self.i_am_leader_callback)
        self.keep_alive = KeepAlive()
        self.active = True
        signal.signal(signal.SIGTERM, self.stop)


    def run(self):
        self.keep_alive.start()
        self.leader_election.run()
        while self.active:
            self.__wait_to_become_leader()
            if not self.active:
                break
            self.__init_restarter()
            logging.debug("action: start_restarter | result: success")
            self.__wait_while_leader()
            self.__join_restarter()

        self.leader_election.stop()
        self.keep_alive.stop()
        self.keep_alive.join()


    def __init_restarter(self):
        # inaccesible containers that must be restarted.
        self.restart_containers_q = queue.Queue()

        # processes with a TCP connection open
        self.connected_processes_q = queue.Queue()

        # containers restarted but with no connection 
        self.create_connections_q = queue.Queue()
        self.__put_containers_create_connections()

        self.docker_restarter = DockerRestarter(self.restart_containers_q, 
                                                self.create_connections_q)

        self.connection_maker = ConnectionMaker(self.create_connections_q,
                                                self.connected_processes_q,
                                                self.restart_containers_q)

        self.healthy_checker = HealthyChecker(self.connected_processes_q,
                                              self.restart_containers_q)

        self.docker_restarter.start()
        self.connection_maker.start()
        self.healthy_checker.start()

    def __join_restarter(self):
        logging.debug("action: stop_restarter | result: in_progress")
        self.docker_restarter.stop()
        self.docker_restarter.join()

        self.connection_maker.stop()
        self.connection_maker.join()

        self.healthy_checker.stop()
        self.healthy_checker.join()
        logging.debug("action: stop_restarter | result: success")


    def __wait_while_leader(self):
        current_state = LEADER
        while current_state == LEADER:
            current_state = self.new_leader_queue.get()
        if current_state == KEEP_ALIVE_ACCEPTED:
            # This could only happen if there are two leaders.
            # It's only possible when there's a new leader and 
            # both packages ELECTION and later COORDINATOR were lost.
            # This is the only possible case (very very unlikely)
            # of two leaders at the same time.
            logging.error("action: processes_restarter_error"
                          "| error: keep_alive_accepted_while_being_leader")
            self.active = False

    def __wait_to_become_leader(self):
        current_state = NO_LEADER
        while current_state == NO_LEADER:
            current_state = self.new_leader_queue.get()

    def stop_being_leader_callback(self):
        self.new_leader_queue.put(NO_LEADER)

    def i_am_leader_callback(self):
        self.new_leader_queue.put(LEADER)

    def keep_alive_accepted_callback(self):
        self.new_leader_queue.put(KEEP_ALIVE_ACCEPTED)

    def __put_containers_create_connections(self):
        for container_name in self.containers_keep_alive:
            self.create_connections_q.put(container_name)

    def stop(self, *args):
        self.active = False
        self.new_leader_queue.put(STOP_LEADER_QUEUE)
