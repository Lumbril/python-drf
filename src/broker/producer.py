from rest_framework import exceptions

from django.conf import settings

import json
import pika
import uuid
import time


class RpcClient(object):

    def __init__(self):
        credentials = pika.PlainCredentials(*settings.BROKER_DATA)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=settings.BROKER_HOST, port=settings.BROKER_PORT,
                heartbeat=600, blocked_connection_timeout=300,
                credentials=credentials
            )
        )
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True, durable=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True
        )

    def on_response(self, ch, method, properties, body):
        if self.corr_id == properties.correlation_id:
            self.response = json.loads(body)
            if self.response.get('error',):
                _, err_type, err_message = self.response.values()
                exception = getattr(exceptions, err_type)
                raise exception(err_message)

    def call(self, key, method, body):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key=key,
            body=json.dumps(body),
            properties=pika.BasicProperties(
                content_type=method,
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            )
        )
        start = time.time()
        while self.response is None and time.time() - start <= 3:
            self.connection.process_data_events()
        self.connection.close()

        if self.response is None and time.time() - start >= 3:
            raise exceptions.APIException('No response received from broker.')
        return self.response
