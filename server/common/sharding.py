import hashlib


class Sharding:
    def __init__(self, amount_nodes_next_stage):
        self.list_nodes = [i for i in range(amount_nodes_next_stage)]
        self.amount_nodes = amount_nodes_next_stage

    def get_shard(self, id_client):
        shard_index = id_client % self.amount_nodes
        return self.list_nodes[shard_index]
