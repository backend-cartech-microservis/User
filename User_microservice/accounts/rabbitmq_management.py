import pika
import json
from queue import Queue
from threading import Thread
from rest_framework_simplejwt.tokens import AccessToken
from bson.objectid import ObjectId
from django.conf import settings
from rest_framework import status
from django.core.cache import cache
import ast

def Rabbitmq_Consumer_AuthUser(exchange_name, queue_name, result_queue):
    result_queue = Queue()
    def callback(ch, method, properties, body):
        headers = properties.headers
        result_queue.put(headers)
        if headers is not None:
            Rabbitmq_Producer_AuthUser(body=AuthMicroserviceUser(jwt_token=headers["JWT"]),
                                exchange_name='User',
                                queue_name='get_order_user',
                                headers={'status':status.HTTP_200_OK})
        else:
            body = Decode_And_Conversion_Dictionary(body=body)
            cache.set(key='Data', value=body,timeout=6)
            cache.close()

        # ch.basic_ack(delivery_tag=method.delivery_tag)
    def start_consumer():
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.exchange_declare(exchange=exchange_name, exchange_type='direct', durable=True)
        channel.queue_declare(queue=queue_name, durable=True)
        channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=queue_name)

        channel.basic_consume(queue=queue_name,
                            on_message_callback=callback,
                            auto_ack=True)

        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()
    consumer_thread = Thread(target=start_consumer)
    consumer_thread.daemon = True
    consumer_thread.start()


def Rabbitmq_Producer_AuthUser(exchange_name, queue_name, body, headers=None):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange_name, exchange_type='direct', durable=True)
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=queue_name)
    # properties = pika.BasicProperties(headers=headers) if headers else None
    channel.basic_publish(exchange=exchange_name,
                        routing_key=queue_name,
                        body=json.dumps(body),
                        properties=pika.BasicProperties(
                            delivery_mode=2,
                            headers={"JWT": headers}  if headers else None
                    ))
    
    connection.close()



def AuthMicroserviceUser(jwt_token):

    try:
        token = AccessToken(jwt_token)
        user_id = token['user_id']
        user_data = settings.USER_COLLECTION.find_one({"_id": ObjectId(user_id)})
        if user_data:
            user_data.pop("password", None)
            user_data['_id'] = str(user_data.get('_id', None))
            user_data['user_id'] = user_id
            return user_data
    except Exception as e:
        print(e)



def Decode_And_Conversion_Dictionary(body):
        body = body.decode('utf-8')
        body = ast.literal_eval(body)
        return body