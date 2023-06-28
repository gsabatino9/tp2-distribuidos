"""
Atomic Storage

This module provides a storage manager that guarantees atomicity to
be able to persist state and be fault tolerant.

Storage is organized in key-value buckets. Each key can have many values associated
with it. Both keys and values must be of type string.
"""

import json, os, tempfile

TMP_FILE_DIR = "./tmp-state"


class AtomicBucket:
    def __init__(self, bucket_id):
        self.bucket_id = bucket_id
        self.data = {}
        os.makedirs(TMP_FILE_DIR, exist_ok=True)
        self._try_load_bucket()

    def _try_load_bucket(self):
        try:
            with open(self._get_bucket_path()) as f:
                self.data = json.load(f)
        except FileNotFoundError:
            pass  # Bucket did not exist.

    def items(self):
        return self.data.items()

    def set(self, key, values):
        self.data[key] = values

    def discard(self, key):
        self.data.pop(key, None)

    def drop(self):
        try:
            os.remove(self._get_bucket_path())
        except OSError:
            pass  # Bucket was never persisted

    def collection(self, collection_name):
        return AtomicBucketCollection(collection_name, self)

    def write_checkpoint(self):
        with tempfile.NamedTemporaryFile(mode="w", dir=os.getcwd(), delete=False) as f:
            json.dump(self.data, f)
            f.flush()
            os.rename(f.name, self._get_bucket_path())

    def _get_bucket_path(self):
        return f"{TMP_FILE_DIR}/{self.bucket_id}"


class AtomicBucketCollection:
    def __init__(self, name, parent_bucket):
        self.name = name
        self.parent_bucket = parent_bucket

    def set(self, key, values):
        self.parent_bucket.set(f"{self.name}#{key}", values)

    def items(self):
        key = f"{self.name}#"
        return map(
            lambda kv: (kv[0][len(key) :], kv[1]),
            filter(lambda kv: kv[0].startswith(key), self.parent_bucket.items()),
        )
