import socket
import logging

IP_ADDR_START = "172.25.125."
IP_ADDR_END_BASE = 4
CONNECTION_PORT = 6767

class Middleware:
    def __init__(self, my_id, n_processes):
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.skt.bind((self.__id_to_ip(my_id), CONNECTION_PORT))
        self.my_id = my_id
        self.n_processes = n_processes

    def recv_message(self):
        msg, addr = self.skt.recvfrom(1)
        process_id = self.__ip_to_id(addr[0])
        logging.debug(f"action: recv_msg | msg: {msg} | from: {process_id}")
        return msg, process_id
    
    def send(self, msg, id_to):
        logging.debug(f"action: send_msg | msg: {msg} | to: {id_to}")
        self.skt.sendto(msg, (self.__id_to_ip(id_to), CONNECTION_PORT))

    def broadcast_bigger(self, msg):
        for id_process in range(self.my_id+1, self.n_processes):
            self.send(msg, id_process)

    def broadcast(self, msg):
        for id_process in range(self.n_processes):
            self.send(msg, id_process)

    def __ip_to_id(self, ip_addr):
        start_splited = IP_ADDR_START.split(".")
        addr = ip_addr.split(".")
        if addr[0] != start_splited[0] or addr[1] != start_splited[1] or addr[2] != start_splited[2]:
            raise Exception("Invalid IP Address.")
        return int(addr[3]) - IP_ADDR_END_BASE

    def __id_to_ip(self, id_process):
        return IP_ADDR_START + str(IP_ADDR_END_BASE+id_process)
