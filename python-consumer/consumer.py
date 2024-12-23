# main.py
import pika
import os
import importlib.util
from config import RABBITMQ, DATABASE, DATE_FORMAT
import traceback
from dbengine import initDB
from applogger import logger

# Function to process messages
def process_message(ch, method, properties, body):
    print(f"Received message from '{method.routing_key}': {body.decode('utf-8')}")

def createMqConnection():
    # Define Credentials
    credentials = pika.PlainCredentials(RABBITMQ.get('username'), RABBITMQ.get('password'))

    # Establish connection to RabbitMQ server
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ.get('ip'), port=RABBITMQ.get('port'), credentials=credentials))
    channel = connection.channel()
    return channel,connection

def createMq(folder_path, channel):
    # Declare an exchange
    exchange_name = RABBITMQ.get('exchange')
    exchange_type = 'direct'

    channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type)
    print(f"Declared exchange '{exchange_name}' of type '{exchange_type}'")

    # List files in the folder
    files = os.listdir(folder_path)
    for filename in files:
        # Construct module name from filename
        if filename !='__pycache__':
            module_name = os.path.splitext(filename)[0]  # Remove .py extension
            module_path = os.path.join(folder_path, filename)
            
            # Dynamically import the consumer module
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Get the process_message function from the module
            process_message_func = getattr(module, "process_message", None)
            if process_message_func:
                queue_name = module_name  # Use filename as queue name for simplicity

                # Declare the queue
                channel.queue_declare(queue=queue_name)
                print(f"Declared Queue: '{queue_name}'")

                # Binding
                channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=f"{queue_name}_key")

                # Set up consumer to use the process_message function
                channel.basic_consume(queue=queue_name, on_message_callback=process_message_func, auto_ack=True)
                print(f"Consuming messages from queue: '{queue_name}'")

                # Start consuming messages
                print(f'Starting to consume messages from queue: {queue_name}')

if __name__ == "__main__":
    try:
        # Establish connection to RabbitMQ
        channel,connection = createMqConnection()
        #Establish Database Connection
        db_status = initDB(DATABASE, DATE_FORMAT)
        if not db_status:
            raise Exception('Database Connection Failed!')
        # Determine the folder containing consumer files
        current_file = os.path.abspath(__file__)
        current_folder = os.path.dirname(current_file)
        consumer_folder = os.path.join(current_folder, 'queues')

        # Create queues and start consuming messages
        createMq(consumer_folder, channel)

        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            print('Interrupted, closing connection...')
            channel.stop_consuming()  # Stop consuming gracefully
            connection.close()  # Close the connection
    except Exception as e:
            logger.critical(traceback.format_exc())
            channel.stop_consuming()  # Stop consuming gracefully
            connection.close()  # Close the connection