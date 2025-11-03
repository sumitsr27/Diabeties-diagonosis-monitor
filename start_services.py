#!/usr/bin/env python
import subprocess
import time
import os
from dotenv import load_dotenv

def start_service(command, name):
    try:
        process = subprocess.Popen(command, shell=True)
        print(f"✅ Started {name}")
        return process
    except Exception as e:
        print(f"❌ Failed to start {name}: {e}")
        return None

def main():
    # Load environment variables
    load_dotenv()
    
    # Start FastAPI server
    fastapi = start_service(
        "uvicorn model_server.app:app --host 0.0.0.0 --port 8000",
        "FastAPI Server"
    )
    
    # Start Streamlit dashboard
    streamlit = start_service(
        "streamlit run dashboard/streamlit_app.py",
        "Streamlit Dashboard"
    )
    
    # Start Kafka producer
    producer = start_service(
        "python kafka_producer/producer_vitals.py",
        "Kafka Producer"
    )
    
    # Start Kafka consumer
    consumer = start_service(
        "python kafka_consumer/consumer_to_hdfs.py",
        "Kafka Consumer"
    )
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping all services...")
        for process in [fastapi, streamlit, producer, consumer]:
            if process:
                process.terminate()
        print("All services stopped.")

if __name__ == "__main__":
    main()