import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODEL_DIR = os.path.join(BASE_DIR, 'models')
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# Model files
MODEL_PATH = os.path.join(MODEL_DIR, 'model.joblib')
SCALER_PATH = os.path.join(MODEL_DIR, 'scaler.joblib')
SHAP_PATH = os.path.join(MODEL_DIR, 'shap_explainer.joblib')

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'vitals')

# HDFS Configuration
HDFS_URL = os.getenv('HDFS_URL', 'http://hdfs-namenode:9870')
HDFS_USER = os.getenv('HDFS_USER', 'root')
HDFS_DIR = os.getenv('HDFS_DIR', '/data/vitals/')

# API Configuration
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '8000'))

# Batch Processing
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '200'))