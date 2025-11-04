#!/usr/bin/env python
"""
Test script to verify Hadoop HDFS connectivity
"""
from hdfs import InsecureClient
import os
from dotenv import load_dotenv

load_dotenv()

HDFS_URL = os.getenv('HDFS_URL', 'http://localhost:9870')
HDFS_USER = os.getenv('HDFS_USER', 'root')
HDFS_DIR = os.getenv('HDFS_DIR', '/data/vitals/')

def test_hdfs_connection():
    try:
        print(f"Attempting to connect to HDFS at {HDFS_URL}...")
        
        # Wait a bit for NameNode to be fully ready
        import time
        time.sleep(5)
        
        client = InsecureClient(HDFS_URL, user=HDFS_USER)
        
        # List root directory
        print("\n✓ Connected to HDFS successfully!")
        print(f"\nRoot directory contents:")
        root_contents = client.list('/')
        for item in root_contents:
            print(f"  - {item}")
        
        # Create vitals directory if it doesn't exist
        print(f"\nCreating directory: {HDFS_DIR}")
        client.makedirs(HDFS_DIR)
        print(f"✓ Directory {HDFS_DIR} is ready")
        
        # Test write
        test_file = f"{HDFS_DIR}test.txt"
        print(f"\nTesting write to {test_file}...")
        with client.write(test_file, overwrite=True) as writer:
            writer.write(b"Hello from Healthcare Pipeline!")
        print("✓ Write test successful")
        
        # Test read
        print(f"\nTesting read from {test_file}...")
        with client.read(test_file) as reader:
            content = reader.read()
            print(f"✓ Read test successful: {content.decode('utf-8')}")
        
        # Clean up
        print(f"\nCleaning up test file...")
        client.delete(test_file)
        print("✓ Cleanup successful")
        
        print("\n" + "="*50)
        print("✅ HDFS is ready for use!")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ HDFS connection failed: {e}")
        print("\nMake sure:")
        print("1. Docker containers are running: docker ps")
        print("2. NameNode is accessible: http://localhost:9870")
        print("3. Run: docker-compose up -d")
        return False

if __name__ == "__main__":
    test_hdfs_connection()
