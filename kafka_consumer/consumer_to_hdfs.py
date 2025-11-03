import json
import logging
from kafka import KafkaConsumer
from hdfs import InsecureClient
import pandas as pd
from io import BytesIO
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration from environment variables
BOOTSTRAP = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
TOPIC = os.getenv('KAFKA_TOPIC', 'vitals')
HDFS_URL = os.getenv('HDFS_URL', 'http://hdfs-namenode:9870')
HDFS_USER = os.getenv('HDFS_USER', 'root')
HDFS_DIR = os.getenv('HDFS_DIR', '/data/vitals/')
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '200'))

# Configure consumer with error handling
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=[BOOTSTRAP],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='vitals_consumer_group',
    consumer_timeout_ms=1000  # timeout after 1 second of no messages
)


# Set up local storage directory
DATA_DIR = os.path.join(os.getcwd(), 'data', 'vitals_data')
os.makedirs(DATA_DIR, exist_ok=True)
logger.info(f"Writing data to local directory: {DATA_DIR}")


def write_batch_to_local(buffer):
    try:
        if not buffer:
            return

        df = pd.DataFrame(buffer)
        fname = os.path.join(DATA_DIR, f"vitals_{int(pd.Timestamp.now().timestamp())}.parquet")
        df.to_parquet(fname, index=False)
        logger.info(f'Wrote {len(buffer)} records to {fname}')
        logger.info(f'Latest vitals data sample: {df.iloc[-1].to_dict()}')

    except Exception as e:
        logger.error(f"Failed to write batch: {e}")
        raise

def main():
    buffer = []
    
    try:
        while True:
            try:
                for msg in consumer:
                    buffer.append(msg.value)
                    if len(buffer) >= BATCH_SIZE:
                        write_batch_to_local(buffer)
                        buffer = []
                
                # Write any remaining records
                if buffer:
                    write_batch_to_local(buffer)
                    buffer = []
                    
            except StopIteration:
                continue
            
    except KeyboardInterrupt:
        logger.info("Stopping consumer...")
        if buffer:
            write_batch_to_local(buffer)
        consumer.close()
        logger.info("Consumer stopped.")

if __name__ == '__main__':
    main()