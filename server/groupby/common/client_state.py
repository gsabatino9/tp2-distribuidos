from server.groupby.common.groupby import Groupby
from server.common.duplicate_filter import DuplicateFilter
from server.common.atomic_storage.atomic_storage import AtomicBucket


class ClientState:
    def __init__(self, id_client, groupby_operation, groupby_base_data):
        self.backing_storage = AtomicBucket(id_client)
        self.groupby = Groupby(
            groupby_operation,
            groupby_base_data,
            self.backing_storage.collection("groupby"),
        )
        self.dup_filter = DuplicateFilter(self.backing_storage.collection("dup_filter"))

    def drop(self):
        """
        Drops the backing storage.
        """
        self.backing_storage.drop()
