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

class ProcessesRestarter:
    def __init__(self, my_id, n_processes, containers_keep_alive, container_restarter_name):
        self.containers_keep_alive = containers_keep_alive
        my_container_name = container_restarter_name + str(my_id)
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
            self.__wait_while(NO_LEADER)
            if not self.active:
                break
            self.__init_restarter()
            self.__wait_while(LEADER)
            self.__join_restarter()

        self.keep_alive.stop()
        self.keep_alive.join()


    def __init_restarter(self):
        # inaccesible containers.
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
        self.docker_restarter.stop()
        self.docker_restarter.join()

        self.connection_maker.stop()
        self.connection_maker.join()

        self.healthy_checker.stop()
        self.healthy_checker.join()


    def __wait_while(self, while_clause):
        value = while_clause
        while value == while_clause:
            value = self.new_leader_queue.get()

    def stop_being_leader_callback(self):
        logging.info("no soy mas leader")
        self.new_leader_queue.put(NO_LEADER)

    def i_am_leader_callback(self):
        logging.info("soy leader")
        self.new_leader_queue.put(LEADER)

    def __put_containers_create_connections(self):
        for container_name in self.containers_keep_alive:
            self.create_connections_q.put(container_name)

    def stop(self, *args):
        self.leader_election.stop()
        self.active = False
        self.new_leader_queue.put(STOP_LEADER_QUEUE)
