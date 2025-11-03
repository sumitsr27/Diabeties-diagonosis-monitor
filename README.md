# Healthcare Pipeline with Real-time Patient Monitoring

## Project Overview
This project implements a real-time healthcare monitoring system that combines streaming data processing, machine learning predictions, and interactive visualization. The system processes patient vitals data through a Kafka pipeline, makes diabetes risk predictions using a trained ML model, and displays results in a real-time dashboard.

## Architecture
![Architecture](docs/architecture.png)

### Components
1. **Data Producer** (`kafka_producer/`)
   - Generates simulated patient vitals data
   - Publishes to Kafka topic "vitals"
   - Metrics: heart rate, SpO2, blood pressure, etc.

2. **Data Consumer** (`kafka_consumer/`)
   - Subscribes to Kafka topic
   - Processes incoming vitals data
   - Stores data in Parquet format
   - Fallback to local storage if HDFS unavailable

3. **Model Server** (`model_server/`)
   - FastAPI-based prediction service
   - Loads trained diabetes prediction model
   - RESTful API endpoints for predictions
   - Input validation and error handling

4. **Dashboard** (`dashboard/`)
   - Streamlit-based interactive dashboard
   - Real-time vitals monitoring
   - Diabetes risk prediction interface
   - SHAP feature importance visualization

5. **Model Training** (`model_training/`)
   - Jupyter notebook for model development
   - Feature engineering and preprocessing
   - Model training and evaluation
   - SHAP explainer generation

## Technology Stack
- **Data Processing**: Apache Kafka
- **ML Framework**: Scikit-learn
- **API**: FastAPI
- **Dashboard**: Streamlit
- **Storage**: Parquet files, HDFS (configurable)
- **Containerization**: Docker
- **Language**: Python 3.x

## Setup and Installation

### Prerequisites
- Docker Desktop
- Python 3.8+
- Java Runtime Environment (JRE)

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows
source venv/bin/activate      # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Starting Services
1. Start Kafka infrastructure:
```bash
docker-compose up -d
```

2. Start the Model Server:
```bash
uvicorn model_server.app:app --reload
```

3. Start the Streamlit Dashboard:
```bash
streamlit run dashboard/streamlit_app.py
```

4. Start Producer and Consumer:
```bash
python kafka_producer/producer_vitals.py
python kafka_consumer/consumer_to_hdfs.py
```

## Project Structure
```
healthcare-pipeline/
├── config.py                 # Configuration settings
├── docker-compose.yml        # Docker services configuration
├── requirements.txt          # Python dependencies
├── connect/
│   └── hdfs-sink-config.json # HDFS connector configuration
├── dashboard/
│   └── streamlit_app.py      # Streamlit dashboard
├── data/
│   ├── pima.csv             # Training dataset
│   └── vitals_data/         # Stored vitals data
├── kafka_consumer/
│   └── consumer_to_hdfs.py  # Kafka consumer implementation
├── kafka_producer/
│   └── producer_vitals.py   # Data generation and producer
├── model_server/
│   └── app.py              # FastAPI model serving
├── model_training/
│   ├── train_model.py      # Model training script
│   └── pima_training.ipynb # Training notebook
└── models/                 # Saved model artifacts
    ├── model.joblib
    ├── scaler.joblib
    └── shap_explainer.joblib
```

## API Documentation
The FastAPI server provides the following endpoints:

- `GET /health`: Health check endpoint
- `POST /predict`: Diabetes risk prediction endpoint

### Prediction Request Format
```json
{
    "pregnancies": 0,
    "glucose": 137,
    "blood_pressure": 40,
    "skin_thickness": 35,
    "insulin": 168,
    "bmi": 43.1,
    "diabetes_pedigree_function": 2.288,
    "age": 33
}
```

## Dashboard Features
1. Real-time Patient Vitals Monitoring
2. Historical Data Visualization
3. Risk Prediction Interface
4. Feature Importance Analysis
5. Patient Statistics

## Data Flow
1. Producer generates simulated patient vitals
2. Data is published to Kafka topic "vitals"
3. Consumer processes and stores data
4. Dashboard reads latest data for visualization
5. Model server provides predictions on demand

## Configuration
Key configuration settings in `config.py`:
- Kafka bootstrap servers
- Topic configurations
- HDFS connection settings
- Model paths
- Batch processing parameters

## Monitoring and Logging
- Logging configured for all components
- Kafka consumer group monitoring
- Model prediction logging
- Dashboard activity tracking

## Future Enhancements
1. Enhanced anomaly detection
2. Multi-model support
3. Advanced visualization features
4. Automated model retraining
5. Extended metrics collection

## Contributing
Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the LICENSE file for details.