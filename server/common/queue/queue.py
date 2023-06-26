import pika, random


class GenericQueue:
    def __init__(self, channel, auto_ack=True):
        self.channel = channel
        self.auto_ack = auto_ack
        self.callback = self.__generic_callback
        self.last_delivery_tag = None

    def __callback(self, ch, method, properties, body):
        self.last_delivery_tag = method.delivery_tag
        self.callback(body)
        if self.auto_ack:
            self.channel.basic_ack(delivery_tag=self.last_delivery_tag)

    def receive_msg(self, queue_name, callback):
        self.callback = callback
        self.channel.basic_consume(
            queue=queue_name, on_message_callback=self.__callback, auto_ack=False
        )

    def __generic_callback(self, body):
        pass

    def ack_all(self):
        self.channel.basic_ack(delivery_tag=self.last_delivery_tag, multiple=True)


class BasicQueue(GenericQueue):
    def __init__(self, channel, queue_name, auto_ack=True):
        super().__init__(channel, auto_ack)
        self.queue_name = queue_name
        self.__build_queue()

    def __build_queue(self):
        self.channel.queue_declare(queue=self.queue_name)

    def receive(self, callback, prefetch_count=1):
        self.channel.basic_qos(prefetch_count=prefetch_count)
        self.receive_msg(self.queue_name, callback)

    def send(self, message):
        self.channel.basic_publish(
            exchange="", routing_key=self.queue_name, body=message
        )


class PubsubQueue(GenericQueue):
    def __init__(self, channel, exchange_name, auto_ack=True):
        super().__init__(channel, auto_ack)
        self.exchange_name = exchange_name
        self.__build_exchange()

    def __build_exchange(self):
        self.channel.exchange_declare(
            exchange=self.exchange_name, exchange_type="fanout"
        )

    def receive(self, callback):
        result = self.channel.queue_declare(queue="", exclusive=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange=self.exchange_name, queue=queue_name)
        self.receive_msg(queue_name, callback)

    def send(self, message):
        self.channel.basic_publish(
            exchange=self.exchange_name, routing_key="", body=message
        )


class PubsubWorkerQueue(GenericQueue):
    def __init__(self, channel, exchange_name, queue_name, auto_ack=True):
        super().__init__(channel, auto_ack)
        self.exchange_name = exchange_name
        self.queue_name = queue_name
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
        self.receive_msg(self.queue_name, callback)


class RoutingQueue(GenericQueue):
    def __init__(self, channel, exchange_name, routing_keys, auto_ack=True):
        super().__init__(channel, auto_ack)
        self.exchange_name = exchange_name
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

    def __callback(self, ch, method, properties, body):
        self.last_delivery_tag = method.delivery_tag
        self.callback(body, method.routing_key)
        if self.auto_ack:
            self.channel.basic_ack(delivery_tag=self.last_delivery_tag)

    def receive(self, callback):
        self.callback = callback
        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=self.__callback, auto_ack=False
        )

    def send(self, message, routing_key):
        self.channel.basic_publish(
            exchange=self.exchange_name, routing_key=routing_key, body=message
        )


class RoutingBuildQueue(GenericQueue):
    def __init__(self, channel, exchange_name, queue_name, auto_ack=True):
        super().__init__(channel, auto_ack)
        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.channel.exchange_declare(
            exchange=self.exchange_name, exchange_type="direct"
        )
        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def bind_queue(self, routing_key):
        self.channel.queue_bind(
            exchange=self.exchange_name, queue=self.queue_name, routing_key=routing_key
        )

    def receive(self, callback):
        self.receive_msg(self.queue_name, callback)

    def send(self, message, routing_key):
        self.channel.basic_publish(
            exchange=self.exchange_name, routing_key=routing_key, body=message
        )

    def broadcast_workers(self, amount_nodes, msg):
        for idx_worker in range(amount_nodes):
            binding_key = self.queue_name + str(idx_worker)
            self.send(msg, routing_key=binding_key)

    def send_worker(self, amount_nodes, msg):
        # se elige un worker de forma random para mandar el mensaje,
        # dentro de todos los posibles workers.
        # parecido a un round-robin.
        idx_worker = random.choice(range(1, amount_nodes + 1))
        binding_key = self.queue_name + str(idx_worker)
        self.send(msg, routing_key=binding_key)
