import time
from server.common.atomic_storage.atomic_storage import AtomicBucket


class SessionManagerState:
    def __init__(self):
        self.sessions = []
        self.bucket = AtomicBucket("session-manager")
        self.__try_recover_state()

    def __try_recover_state(self):
        aux = list(self.bucket.items())
        if aux:
            self.sessions = aux[0][1]

    def add_client(self, id_client):
        self.sessions.append([id_client, time.time(), False])
        self.bucket.set("sessions", self.sessions)

    def get_expired_sessions(self, limit_time):
        expired_sessions = []

        time_now = time.time()
        for id_client, tmp, is_deleting in self.sessions:
            if (time_now - tmp) > limit_time and (not is_deleting):
                expired_sessions.append(id_client)

        return expired_sessions

    def is_deleting_client(self, id_client):
        for i, (id_client_tmp, tmp, is_deleting) in enumerate(self.sessions):
            if (id_client_tmp == id_client) and (not is_deleting):
                return True

        return False

    def mark_start_deleting(self, id_client):
        for i, (id_client_tmp, tmp, is_deleting) in enumerate(self.sessions):
            if (id_client_tmp == id_client) and (not is_deleting):
                self.sessions[i] = [id_client, tmp, True]
                self.bucket.set("sessions", self.sessions)

    def count_clients(self):
        return len(self.sessions)

    def delete_client(self, id_client):
        for i, (id_client_tmp, tmp, is_deleting) in enumerate(self.sessions):
            if (id_client_tmp == id_client) and is_deleting:
                del self.sessions[i]
                self.bucket.set("sessions", self.sessions)
                print(f"action: end_session | result: success | id_client: {id_client}")
                return

    def write_checkpoint(self):
        self.bucket.write_checkpoint()
