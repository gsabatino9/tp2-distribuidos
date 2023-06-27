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

class MultipleQueues(GenericQueue):
    def __init__(self, channel, names_queues, amount_nodes, auto_ack=True):
        super().__init__(channel, auto_ack)
        self.names_queues = names_queues
        self.amount_nodes = amount_nodes
        self.list_workers = [0 for _ in self.amount_nodes]

        self.__build_queues()

    def __build_queues(self):
        for i, name_queue in enumerate(self.names_queues):
            for idx_worker in range(1, self.amount_nodes[i]+1):
                name_queue += str(idx_worker)
                self.channel.queue_declare(queue=name_queue)

    def send(self, message):
        for i, name_queue in enumerate(self.names_queues):
            # we use round-robin
            idx_worker = (self.list_workers[i] % self.amount_nodes[i])+1
            self.channel.basic_publish(
                exchange="", routing_key=name_queue+str(idx_worker), body=message
            )
            self.list_workers[i] += 1

    def broadcast(self, message):
        for i, name_queue in enumerate(self.names_queues):
            for idx_worker in range(1, self.amount_nodes[i]+1):
                self.channel.basic_publish(
                    exchange="", routing_key=name_queue+str(idx_worker), body=message
                )


class ShardingQueue(GenericQueue):
    """
    si tenemos N workers que deben recibir data estática y ejecutar
    tareas sobre esa data estática, usamos un subconjunto de estos workers
    para enviar la data estática.
    Luego, elegimos, sobre ese subconjunto, 1 de ellos (al azar) en cada envío.
    """

    def __init__(self, channel, name_queue, amount_nodes, sharding_amount, auto_ack=True):
        super().__init__(channel, auto_ack)
        self.name_queue = name_queue
        self.amount_nodes = amount_nodes
        self.sharding_amount = sharding_amount

        self.__build_queues()

    def __build_queues(self):
        for idx_worker in range(1, self.amount_nodes+1):
            self.channel.queue_declare(queue=self.name_queue+str(idx_worker))

    def __get_shards(self, id_client):
        start_idx = id_client % self.amount_nodes
        list_idxs = []

        for i in range(start_idx, start_idx+self.sharding_amount):
            name_queue = self.name_queue + str((i % self.amount_nodes)+1)
            list_idxs.append(name_queue)

        return list_idxs

    def send_static(self, msg, id_client):
        list_shards = self.__get_shards(id_client)
        for name_queue in list_shards:
            self.channel.basic_publish(
                exchange="", routing_key=name_queue, body=msg
            )

    def send_workers(self, msg, id_client):
        list_shards = self.__get_shards(id_client)
        self.channel.basic_publish(
            exchange="", routing_key=random.choice(list_shards), body=msg
        )