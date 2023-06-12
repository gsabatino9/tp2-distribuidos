from common.leader_election.utils import Message
import threading
import logging

class ControlReceiver(threading.Thread):
    def __init__(self, my_id, middleware, election_starter, control_sender, leader_alive,
                       stop_being_leader_callback, i_am_leader_callback):
        super().__init__()
        self.my_id = my_id
        self.middleware = middleware
        self.election_starter = election_starter
        self.control_sender = control_sender
        self.leader_alive = leader_alive
        self.stop_being_leader_callback = stop_being_leader_callback
        self.i_am_leader_callback = i_am_leader_callback
        self.active = True

    def run(self):
        try:
            self.__run_loop()
        except Exception as e:
            if not self.active:
                return
            logging.error(f"action: control_receiver_error | error: {str(e)}")
        except:
            if not self.active:
                return
            logging.error(f"action: control_receiver_error | error: unknown")
            

    def __run_loop(self):
        while (self.active):
            msg, id_from = self.middleware.recv_message()
            if msg == Message.ELECTION.value:
                self.__handle_election(id_from)
            elif msg == Message.COORDINATOR.value:
                self.__handle_coordinator(id_from)
            elif msg == Message.ELECTION_ACK.value:
                self.__handle_election_ack(id_from)
            elif msg == Message.LEADER_ALIVE.value:
                self.__handle_leader_alive(id_from)
            elif msg == Message.LEADER_ALIVE_REPLY.value:
                self.__handle_leader_alive_reply(id_from)
            else:
                raise Exception("Invalid Message Received")

    def stop(self):
        if not self.active:
            logging.error(f"action: control_receiver_error | error: already_stopped")
            return
        self.active = False
        self.middleware.stop()

    def __handle_election(self, id_from):
        self.stop_being_leader_callback()
        if id_from >= self.my_id:
            logging.error(f"action: control_receiver_error | error: "
                          f"election_from_bigger_received | from: {id_from}")
            return    
        self.control_sender.send_election_ack(id_from)
        self.election_starter.start_election()

    def __handle_coordinator(self, id_from):
        if id_from == self.my_id:
            self.i_am_leader_callback()
        else:
            self.stop_being_leader_callback()
        self.election_starter.coordinator_received(id_from)
        self.leader_alive.coordinator_received(id_from)

    def __handle_election_ack(self, id_from):
        self.election_starter.election_ack()

    def __handle_leader_alive(self, id_from):
        self.leader_alive.leader_alive_received(id_from)

    def __handle_leader_alive_reply(self, id_from):
        self.leader_alive.leader_alive_reply_received(id_from)
