import json
import logging
from kafka import KafkaConsumer
try:
    from hdfs import InsecureClient
except ImportError:
    InsecureClient = None
import pandas as pd
from io import BytesIO
from dotenv import load_dotenv
import os
import time

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
# Flush interval in seconds to force-write partial batches for near-real-time updates
BATCH_FLUSH_SECS = int(os.getenv('BATCH_FLUSH_SECS', '5'))

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


# Set up local storage directory as fallback
DATA_DIR = os.path.join(os.getcwd(), 'data', 'vitals_data')
os.makedirs(DATA_DIR, exist_ok=True)

# Try to connect to HDFS
try:
    if InsecureClient is None:
        raise ImportError("hdfs client not installed")
    hdfs_client = InsecureClient(HDFS_URL, user=HDFS_USER)
    # Test HDFS connection
    hdfs_client.list('/')
    logger.info(f"Successfully connected to HDFS at {HDFS_URL}")
    USE_HDFS = True
except Exception as e:
    logger.warning(f"HDFS not available ({e}), falling back to local storage: {DATA_DIR}")
    hdfs_client = None
    USE_HDFS = False
    logger.info(f"Writing data to local directory: {DATA_DIR}")


def write_batch_to_hdfs(buffer):
    """Write batch data to HDFS"""
    try:
        if not buffer:
            return

        df = pd.DataFrame(buffer)
        timestamp = int(pd.Timestamp.now().timestamp())
        hdfs_path = f"{HDFS_DIR}vitals_{timestamp}.parquet"
        
        # Write to buffer first
        parquet_buffer = BytesIO()
        df.to_parquet(parquet_buffer, index=False)
        parquet_buffer.seek(0)
        
        # Upload to HDFS
        with hdfs_client.write(hdfs_path, overwrite=True) as writer:
            writer.write(parquet_buffer.read())
        
        logger.info(f'Wrote {len(buffer)} records to HDFS: {hdfs_path}')
        logger.info(f'Latest vitals data sample: {df.iloc[-1].to_dict()}')

    except Exception as e:
        logger.error(f"Failed to write batch to HDFS: {e}")
        # Fallback to local storage
        write_batch_to_local(buffer)


def write_batch_to_local(buffer):
    try:
        if not buffer:
            return

        df = pd.DataFrame(buffer)
        fname = os.path.join(DATA_DIR, f"vitals_{int(pd.Timestamp.now().timestamp())}.parquet")
        df.to_parquet(fname, index=False)
        logger.info(f'Wrote {len(buffer)} records to local: {fname}')
        logger.info(f'Latest vitals data sample: {df.iloc[-1].to_dict()}')

    except Exception as e:
        logger.error(f"Failed to write batch to local: {e}")
        raise

def main():
    buffer = []
    write_func = write_batch_to_hdfs if USE_HDFS else write_batch_to_local
    last_flush_ts = time.time()

    try:
        while True:
            try:
                for msg in consumer:
                    buffer.append(msg.value)

                    # Condition 1: flush on batch size
                    if len(buffer) >= BATCH_SIZE:
                        write_func(buffer)
                        buffer = []
                        last_flush_ts = time.time()

                    # Condition 2: time-based flush for near-real-time updates
                    now = time.time()
                    if buffer and (now - last_flush_ts) >= BATCH_FLUSH_SECS:
                        write_func(buffer)
                        buffer = []
                        last_flush_ts = now

                # End of current poll: perform time-based flush if needed
                now = time.time()
                if buffer and (now - last_flush_ts) >= BATCH_FLUSH_SECS:
                    write_func(buffer)
                    buffer = []
                    last_flush_ts = now

            except StopIteration:
                # No more messages right now; still respect time-based flush
                now = time.time()
                if buffer and (now - last_flush_ts) >= BATCH_FLUSH_SECS:
                    write_func(buffer)
                    buffer = []
                    last_flush_ts = now
                continue

    except KeyboardInterrupt:
        logger.info("Stopping consumer...")
        if buffer:
            write_func(buffer)
        consumer.close()
        logger.info("Consumer stopped.")

if __name__ == '__main__':
    main()