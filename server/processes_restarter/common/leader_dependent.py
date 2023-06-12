import queue

class LeaderDependent:
    def __init__(self):
        self.active = True
        self.new_leader_queue = queue.Queue()
        self.stop_confirmation = queue.Queue()
        self.i_am_leader = False

    def wait_until_leader(self):
        msg = self.new_leader_queue.get()

    def new_leader_notified(self):
        self.i_am_leader = True
        # Notify new leader
        self.new_leader_queue.put(None)

    def stop_waiting(self):
        self.active = False
        self.i_am_leader = False
        self.new_leader_queue.put(None)

    def send_stop_confirmation(self):
        self.stop_confirmation.put(None)

    def wait_until_stop_confirmation(self):
        msg = self.stop_confirmation.get()
