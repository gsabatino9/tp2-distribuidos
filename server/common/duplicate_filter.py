class DuplicateFilter:
    def __init__(self, backing_storage=None):
        self.max_batch_seen = -1
        self.missing_batches = set()

        self.backing_storage = backing_storage
        if self.backing_storage:
            self.__try_recover_state()

    def __try_recover_state(self):
        for key, item in self.backing_storage.items():
            if key == "max_batch_seen":
                self.max_batch_seen = item
            elif key == "missing_batches":
                self.missing_batches = set(item)
            else:
                print(
                    f"action: dup_filter_recover | result: invalid data | data: {key}"
                )

    def mark_as_seen(self, value):
        if value in self.missing_batches:
            self.missing_batches.discard(value)
        elif value <= self.max_batch_seen:
            return
        else:
            for missing_batch in range(self.max_batch_seen + 1, value):
                self.missing_batches.add(missing_batch)
            self.max_batch_seen = value

        if self.backing_storage:
            self.backing_storage.set("missing_batches", list(self.missing_batches))
            self.backing_storage.set("max_batch_seen", self.max_batch_seen)

    def has_been_seen(self, value):
        return value <= self.max_batch_seen and value not in self.missing_batches


def _test_dup_filter():
    d = DuplicateFilter()

    assert not d.has_been_seen(0)
    assert not d.has_been_seen(1)
    assert not d.has_been_seen(500)

    d.mark_as_seen(0)
    assert d.has_been_seen(0)
    assert not d.has_been_seen(1)
    assert not d.has_been_seen(500)

    d.mark_as_seen(1)
    assert d.has_been_seen(0)
    assert d.has_been_seen(1)
    assert not d.has_been_seen(500)

    d.mark_as_seen(10)
    assert d.has_been_seen(0)
    assert d.has_been_seen(1)
    assert not d.has_been_seen(2)
    assert not d.has_been_seen(9)
    assert d.has_been_seen(10)
    assert not d.has_been_seen(11)
    assert not d.has_been_seen(500)

    return d
