import threading
import time
import queue
import logging
import socket
from common.utils import ARE_YOU_ALIVE_MESSAGE, HEALTHCHECK_TIMEOUT,\
                         MINIMUM_TIMEOUT_TIME, TIME_BETWEEN_HEALTHCHECKS

class HealthyChecker(threading.Thread):
    def __init__(self, connected_processes_q, restart_containers_q):
        super().__init__()
        self.connected_processes_q = connected_processes_q
        self.restart_containers_q = restart_containers_q
        self.active = True

    def run(self):
        try:
            self.__execute_healthcheck_operations()
        except Exception as e:
            logging.error(f"action: healthy_checker_error | error: {str(e)}")
        except:
            logging.error(f"action: healthy_checker_error | error: unknown")
        finally:
            self.__free_resources()

    def __execute_healthcheck_operations(self):
        while self.active:
            container, skt, send_time = self.connected_processes_q.get()
            if not container:
                if self.active:
                    logging.error(f"action: healthy_checker_error | error: container_is_none")
                continue
            try:
                self.__wait_for_healthcheck_reply(container, skt, send_time)
            except Exception as e:
                logging.error(f"action: healthy_checker_timeout | container: {container}")
                skt.shutdown(socket.SHUT_RDWR)
                skt.close()
                self.restart_containers_q.put(container)


    def __wait_for_healthcheck_reply(self, container, skt, send_time):
        waited_time = time.time() - send_time
        timeout_time = max(HEALTHCHECK_TIMEOUT - waited_time, MINIMUM_TIMEOUT_TIME)
        skt.settimeout(timeout_time)
        a = skt.recv(1)
        if not a:
            raise Exception("No message received")
        logging.debug(f"action: keep_alive_loop | result: success"
                      f" | container: {container}")
        constant_time_loop = max(TIME_BETWEEN_HEALTHCHECKS - (time.time() - send_time), 0.0)
        time.sleep(constant_time_loop)
        skt.sendall(ARE_YOU_ALIVE_MESSAGE)
        self.connected_processes_q.put((container, skt, time.time()))

    def __free_resources(self):
        try:
            while True:
                container, skt, send_time = self.connected_processes_q.get_nowait()
                if skt:
                    try:
                        skt.shutdown(socket.SHUT_RDWR)
                    except OSError:
                        # shutdown fails if connection is already shutdown.
                        pass
                    skt.close()
        except queue.Empty:
            # all items in connected_q removed
            pass


    def stop(self):
        self.active = False
        self.connected_processes_q.put((None, None, None))
