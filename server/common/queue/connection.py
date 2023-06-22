import pika, sys, os
from server.common.queue.queue import (
    BasicQueue,
    PubsubQueue,
    RoutingQueue,
    RoutingBuildQueue,
    PubsubWorkerQueue,
)


class Connection:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
        self.channel = self.connection.channel()

    def basic_queue(self, name_queue, auto_ack=True):
        return BasicQueue(self.channel, name_queue, auto_ack=auto_ack)

    def pubsub_queue(self, name_exchange, auto_ack=True):
        return PubsubQueue(self.channel, name_exchange, auto_ack=auto_ack)

    def pubsub_worker_queue(self, name_exchange, name_queue, auto_ack=True):
        return PubsubWorkerQueue(
            self.channel, name_exchange, name_queue, auto_ack=auto_ack
        )

    def routing_queue(self, exchange_name, routing_keys=[], auto_ack=True):
        return RoutingQueue(
            self.channel, exchange_name, routing_keys, auto_ack=auto_ack
        )

    def routing_build_queue(self, exchange_name, queue_name, routing_keys=[]):
        return RoutingBuildQueue(self.channel, exchange_name, queue_name, routing_keys)

    def start_receiving(self):
        self.channel.start_consuming()

    def stop_receiving(self):
        self.channel.stop_consuming()

    def delete_queue(self, queue_name):
        self.channel.queue_delete(queue=queue_name)

    def close(self):
        self.connection.close()
