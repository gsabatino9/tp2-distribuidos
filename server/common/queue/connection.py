import pika, sys, os
from server.common.queue.queue import (
    BasicQueue,
    RoutingQueue,
    RoutingBuildQueue,
    MultipleQueues,
    ShardingQueue,
    PubsubQueue
)


class Connection:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
        self.channel = self.connection.channel()

    def basic_queue(self, name_queue, auto_ack=True):
        return BasicQueue(self.channel, name_queue, auto_ack=auto_ack)

    def routing_queue(self, exchange_name, routing_keys=[], auto_ack=True):
        return RoutingQueue(
            self.channel, exchange_name, routing_keys, auto_ack=auto_ack
        )

    def routing_building_queue(self, exchange_name, queue_name):
        return RoutingBuildQueue(self.channel, exchange_name, queue_name)

    def multiple_queues(self, names_queues, amount_nodes):
        return MultipleQueues(self.channel, names_queues, amount_nodes)

    def pubsub_queue(self, name_exchange, auto_ack=True):
        return PubsubQueue(self.channel, name_exchange, auto_ack=auto_ack)

    def sharding_queue(self, name_queue, amount_nodes, sharding_amount):
        return ShardingQueue(self.channel, name_queue, amount_nodes, sharding_amount)

    def start_receiving(self):
        self.channel.start_consuming()

    def stop_receiving(self):
        self.channel.stop_consuming()

    def delete_queue(self, queue_name):
        self.channel.queue_delete(queue=queue_name)

    def close(self):
        self.connection.close()
