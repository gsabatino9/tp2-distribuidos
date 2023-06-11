import time
import socket
import threading
import queue
import logging
from common.leader_dependent import LeaderDependent
from common.utils import ARE_YOU_ALIVE_MESSAGE, CONNECTION_PORT, INIT_TIME_SLEEP, MAX_TIME_SLEEP

class ConnectionMaker(threading.Thread, LeaderDependent):
    def __init__(self, create_connections_q, connected_processes_q):
        threading.Thread.__init__(self)
        LeaderDependent.__init__(self)
        self.create_connections_q = create_connections_q
        self.connected_processes_q = connected_processes_q

    def run(self):
        try:
            while self.active:
                self.wait_until_leader()
                self.__execute_create_connections_operations()
                self.__free_leader_resources()
        except Exception as e:
            logging.error(f"action: connection_maker_error | error: {str(e)}")
        except:
            logging.error(f"action: connection_maker_error | error: unknown")


    def __execute_create_connections_operations(self):
        while self.active and self.i_am_leader:
            container_name = self.create_connections_q.get()
            if not container_name:
                if self.i_am_leader:
                    logging.error(f"action: connection_maker_error | error: container_is_none")
                continue
            self.__create_connection(container_name)


    def __create_connection(self, container_addr):
        sleep_time = INIT_TIME_SLEEP
        while self.active and self.i_am_leader:
            try:
                # avoid busy waiting. Restart 
                time.sleep(sleep_time)
                skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                skt.connect((container_addr, CONNECTION_PORT))
                skt.sendall(ARE_YOU_ALIVE_MESSAGE)
                self.connected_processes_q.put((container_addr, skt, time.time()))
                return
            except Exception as e:
                print(f"Error: {str(e)}")
                # Always try again until max time is waited.
                if sleep_time == MAX_TIME_SLEEP:
                    print("ERRORRRR")
                    return
                sleep_time = min(sleep_time * 2, MAX_TIME_SLEEP)
                pass


    def stop_being_leader(self):
        self.i_am_leader = False
        self.create_connections_q.put(None)


    def __free_leader_resources(self):
        try:
            while True:
                container_name = self.create_connections_q.get_nowait()
        except queue.Empty:
            # all items in create_connections_q removed (i am no longer leader)
            pass

    def stop(self):
        # If it's blocked in leader waiting.
        self.stop_waiting()
        # If it's blocked in get container.
        self.stop_being_leader()
