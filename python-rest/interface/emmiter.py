import pika
import json
from config import RABBITMQ
import traceback

class analysis_emmiter:
    def __init__(self,options):
        global logger
        logger = options['logger']

    def ma_rsi(self,data):
        try:
            channel,connection = self.create_channel('ma_rsi_analysis')
            # Message to be sent (convert Python dictionary to JSON)
            message = json.dumps(data)

            # Publish the message to the queue
            channel.basic_publish(exchange='pyconsumer',
                                routing_key='ma_rsi_analysis_key',
                                body=message)
            # Close connection
            connection.close()
            return {"status":"success", "message":f"Sent message to Consumer: Moving Average and  Relative Strength Index"}
        except Exception as e:
            logger.critical(traceback.format_exc())
            err = str(e.args[0]).replace("'","`").replace('"',"`")
            return {"status":"unsuccess", "error":f"Exception: {err}"}
    def correlation(self,data):
        try:
            channel,connection = self.create_channel('correlation_analysis')
            # Message to be sent (convert Python dictionary to JSON)
            message = json.dumps(data)

            # Publish the message to the queue
            channel.basic_publish(exchange='pyconsumer',
                                routing_key='correlation_analysis_key',
                                body=message)
            # Close connection
            connection.close()
            return {"status":"success", "message":f"Sent message to Consumer: Correlation Analysis"}
        except Exception as e:
            logger.critical(traceback.format_exc())
            err = str(e.args[0]).replace("'","`").replace('"',"`")
            return {"status":"unsuccess", "error":f"Exception: {err}"}
    def create_channel(self,queue_name):
        try:
            #Get Data
            RABBITMQ_USERNAME = RABBITMQ.get('username')
            RABBITMQ_PASSWORD = RABBITMQ.get('password')
            RABBITMQ_HOST = RABBITMQ.get('ip')
            RABBITMQ_PORT = RABBITMQ.get('port')
            RABBITMQ_QUEUE = queue_name
            # Establish connection to RabbitMQ server
            credentials = pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
            parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials)
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()

            # Declare a queue (make sure it matches the one the consumer is listening to)
            channel.queue_declare(queue=RABBITMQ_QUEUE)
            return channel,connection
        except Exception as e:
            logger.critical(traceback.format_exc())
            return None,None