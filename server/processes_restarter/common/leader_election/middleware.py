import socket
import logging
from common.leader_election.utils import CONNECTION_PORT

MSG_TO_WAKE_RECVFROM = b"W"
import random


class Middleware:
    def __init__(self, my_id, n_processes, network_problems, ip_base):
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip_base_start = ip_base.split(".")[0:-1]
        self.ip_base_end = int(ip_base.split(".")[-1])
        self.my_hostname = self.__id_to_ip(my_id)
        self.skt.bind((self.my_hostname, CONNECTION_PORT))
        self.my_id = my_id
        self.n_processes = n_processes
        self.active = True
        self.network_problems = network_problems

    def recv_message(self):
        self.__validate_active()
        msg, addr = self.skt.recvfrom(1)
        if len(msg) == 0:
            raise Exception("No message received in recvfrom.")
        if not self.active:
            raise Exception("Middleware was stopped.")
        process_id = self.__ip_to_id(addr[0])
        return msg, process_id

    def send(self, msg, id_to):
        self.__validate_active()
        if random.random() > 0.9 and id_to != self.my_id and self.network_problems:
            logging.info(f"se pierde el mensaje {msg} a {id_to}")
            return
        sent = self.skt.sendto(msg, (self.__id_to_ip(id_to), CONNECTION_PORT))
        if sent != len(msg):
            self.stop()
            raise Exception(
                f"action: sento_failed | bytes_sent: {sent} | len_msg: {len(msg)}."
            )

    def broadcast(self, msg):
        for id_process in range(self.n_processes):
            self.send(msg, id_process)

    def stop(self):
        if self.active:
            self.active = False
            self.skt.sendto(MSG_TO_WAKE_RECVFROM, (self.my_hostname, CONNECTION_PORT))

    def close(self):
        self.skt.close()

    def __validate_active(self):
        if not self.active:
            raise Exception("Middleware was stopped.")

    def __ip_to_id(self, ip_addr):
        start_splited = self.ip_base_start
        addr = ip_addr.split(".")
        if (
            addr[0] != start_splited[0]
            or addr[1] != start_splited[1]
            or addr[2] != start_splited[2]
        ):
            raise Exception("Invalid IP Address.")
        return int(addr[3]) - self.ip_base_end

    def __id_to_ip(self, id_process):
        return ".".join(self.ip_base_start) + "." + str(self.ip_base_end + id_process)
