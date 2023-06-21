import pika


class BasicQueue:
    def __init__(self, channel, queue_name, auto_ack=True):
        self.channel = channel
        self.queue_name = queue_name
        self.auto_ack = auto_ack
        self.__build_queue()

    def __build_queue(self):
        self.channel.queue_declare(queue=self.queue_name)

    def receive(self, callback):
        self.channel.basic_qos(prefetch_count=1)

        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=callback, auto_ack=self.auto_ack
        )

    def send(self, message):
        self.channel.basic_publish(
            exchange="", routing_key=self.queue_name, body=message
        )


class PubsubQueue:
    def __init__(self, channel, exchange_name, auto_ack=True):
        self.channel = channel
        self.exchange_name = exchange_name
        self.auto_ack = auto_ack
        self.__build_exchange()

    def __build_exchange(self):
        self.channel.exchange_declare(
            exchange=self.exchange_name, exchange_type="fanout"
        )

    def receive(self, callback):
        result = self.channel.queue_declare(queue="", exclusive=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange=self.exchange_name, queue=queue_name)

        self.channel.basic_consume(
            queue=queue_name, on_message_callback=callback, auto_ack=self.auto_ack
        )

    def send(self, message):
        self.channel.basic_publish(
            exchange=self.exchange_name, routing_key="", body=message
        )


class PubsubWorkerQueue:
    def __init__(self, channel, exchange_name, queue_name, auto_ack=True):
        self.channel = channel
        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.auto_ack = auto_ack
        self.__build_queue()

    def __build_queue(self):
        self.channel.exchange_declare(
            exchange=self.exchange_name, exchange_type="fanout"
        )

        self.channel.queue_declare(queue=self.queue_name)

        self.channel.queue_bind(
            exchange=self.exchange_name, queue=self.queue_name, routing_key=""
        )

    def receive(self, callback):
        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=callback, auto_ack=self.auto_ack
        )


class RoutingQueue:
    def __init__(self, channel, exchange_name, routing_keys, auto_ack=True):
        self.channel = channel
        self.exchange_name = exchange_name
        self.auto_ack = auto_ack
        self.__build_queue(routing_keys)

    def __build_queue(self, routing_keys):
        self.channel.exchange_declare(
            exchange=self.exchange_name, exchange_type="direct"
        )

        result = self.channel.queue_declare(queue="", exclusive=True)
        self.queue_name = result.method.queue

        for routing_key in routing_keys:
            self.channel.queue_bind(
                exchange=self.exchange_name,
                queue=self.queue_name,
                routing_key=routing_key,
            )

    def receive(self, callback):
        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=callback, auto_ack=self.auto_ack
        )

    def send(self, message, routing_key):
        self.channel.basic_publish(
            exchange=self.exchange_name, routing_key=routing_key, body=message
        )


class RoutingBuildQueue:
    def __init__(
        self, channel, exchange_name, queue_name, routing_keys=[], auto_ack=True
    ):
        self.channel = channel
        self.exchange_name = exchange_name
        self.auto_ack = auto_ack
        self.queue_name = queue_name
        self.__build_exchange()
        self.__build_queues(routing_keys)

    def __build_exchange(self):
        self.channel.exchange_declare(
            exchange=self.exchange_name, exchange_type="direct"
        )

        self.channel.queue_declare(queue=self.queue_name)

    def __build_queues(self, routing_keys):
        if len(routing_keys) == 0:
            self.channel.queue_bind(
                exchange=self.exchange_name,
                queue=self.queue_name,
            )
        else:
            for routing_key in routing_keys:
                self.channel.queue_bind(
                    exchange=self.exchange_name,
                    queue=self.queue_name,
                    routing_key=routing_key,
                )

    def receive(self, callback):
        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=callback, auto_ack=self.auto_ack
        )

    def send(self, message, routing_key):
        self.channel.basic_publish(
            exchange=self.exchange_name, routing_key=routing_key, body=message
        )
