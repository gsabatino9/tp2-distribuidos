from server.groupby.common.groupby import Groupby
from server.common.duplicate_filter import DuplicateFilter


class ClientState:
    def __init__(self, groupby_operation, groupby_base_data, backing_storage=None):
        self.groupby = Groupby(groupby_operation, groupby_base_data, backing_storage)
        self.dup_filter = DuplicateFilter(backing_storage)
