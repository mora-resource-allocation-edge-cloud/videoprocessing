from kafka import KafkaConsumer, KafkaProducer
from subprocess import check_output
import time
import logging 
import os
import sys

initialized = False
MAIN_TOPIC = os.environ.get('KAFKA_MAIN_TOPIC')
ADDRESS = os.environ.get('KAFKA_ADDRESS')

while not initialized:
    try:
        producer = KafkaProducer(bootstrap_servers=ADDRESS)

        consumer = KafkaConsumer(
            bootstrap_servers=ADDRESS,
            group_id='videoprocessing-consumer-group',
            max_poll_interval_ms=10000000
        )

        initialized = True
        logging.warning("Producer connected to Kafka")
    except:
        logging.warning("Producer connection error, retrying...")
        time.sleep(3)

I = 10
while MAIN_TOPIC not in consumer.topics():
    time.sleep(1)
    logging.warning(f"Waiting for the topic ${MAIN_TOPIC} to be created")
    if I > 0:
        I -= 1
    else:
        sys.exit(1)
    
consumer.subscribe(topics=[MAIN_TOPIC])


## ALESKA: Again, it could be multithread
for msg in consumer:
    command, id = msg.value.decode("utf-8").split('|')
    logging.warning(command)
    if command == 'process':
        try:
            stdout = check_output(['./script.sh', id]).decode('utf-8')
            producer.send('processing-topic', bytes(f'processed|{id}', 'utf-8'))
        except Exception as e:
            producer.send('processing-topic', bytes(f'processingFailed|{id}', 'utf-8'))
