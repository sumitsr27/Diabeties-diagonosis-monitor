import time
import json
from kafka import KafkaProducer
import random
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOOTSTRAP = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
TOPIC = os.getenv('KAFKA_TOPIC', 'vitals')

# Configure producer with retry settings
producer = KafkaProducer(
    bootstrap_servers=[BOOTSTRAP],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    retries=5,
    retry_backoff_ms=1000
)


def gen_vital():
    return {
        'patient_id': str(uuid.uuid4())[:8],
        'timestamp': int(time.time()),
        'heart_rate': random.randint(50, 140),
        'spo2': random.randint(85, 100),
        'systolic': random.randint(90, 180),
        'diastolic': random.randint(60, 110),
        'respiratory_rate': random.randint(10, 30)
    }


if __name__ == '__main__':
    try:
        while True:
            rec = gen_vital()
            producer.send(TOPIC, rec)
            print('sent', rec)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping producer...")
        producer.close()
        print("Producer stopped.")