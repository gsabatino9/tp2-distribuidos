class DuplicateFilter:
    def __init__(self, backing_storage=None):
        self.seen = set()
        self.backing_storage = backing_storage
        if self.backing_storage:
            self.__try_recover_state()
    
    def __try_recover_state(self):
        raise NotImplementedError

    def mark_as_seen(self, value):
        self.seen.add(value)
    
    def has_been_seen(self, value):
        return value in self.seen
    