import json
import pika
import multiprocessing


def on_request(ch, method, properties, body):
    from .responses import (
        create_player, create_storage,
        create_currency
    )

    data = json.loads(body)

    if properties.content_type == 'create_player':
        response = create_player(data)
    elif properties.content_type == 'create_storage':
        response = create_storage(data)
    elif properties.content_type == 'create_currency':
        response = create_currency(data)

    if response is None:
        response = {'error': False}

    ch.basic_publish(
        exchange='',
        routing_key=properties.reply_to,
        body=json.dumps(response),
        properties=pika.BasicProperties(
            correlation_id=properties.correlation_id
        )
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)

def connection():
    from django.conf import settings
    from django.apps import apps

    if not apps.apps_ready:
        import django
        django.setup()

    credentials = pika.PlainCredentials(*settings.BROKER_DATA)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=settings.BROKER_HOST, port=settings.BROKER_PORT,
            heartbeat=600, blocked_connection_timeout=300,
            credentials=credentials
        )
    )
    channel = connection.channel()

    channel.queue_declare(queue='core')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='core', on_message_callback=on_request)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print('Shutdown listening message-broker')
        channel.stop_consuming()
        connection.close()

def start():
    is_daemon = multiprocessing.current_process().daemon
    if is_daemon:
        return

    multiprocessing.Process(
        target=connection,
        daemon=True
    ).start()
