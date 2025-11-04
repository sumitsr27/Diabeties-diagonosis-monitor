# 🏥 Real-Time Healthcare Monitoring System using Kafka and HDFS

## 🧠 Problem Statement

Healthcare facilities often struggle with:

- **Delayed response** to critical patient vitals changes
- **Manual monitoring** leading to potential oversight
- **Lack of predictive insights** for diabetes risk assessment
- **Inefficient data management** of patient records
- **No real-time visualization** of patient health metrics

Hence, there is a need for a **real-time intelligent system** that continuously monitors patient vitals, predicts health risks, and provides actionable insights through an interactive dashboard.

---

## 🎯 Objective

To design and implement a **real-time healthcare data pipeline** using **Apache Kafka**, **Hadoop HDFS**, and **Machine Learning** to:

✅ Ingest live patient vitals data continuously  
✅ Store historical health records for analysis  
✅ Predict diabetes risk using ML models  
✅ Visualize real-time patient metrics on an interactive dashboard  
✅ Provide explainable AI insights with SHAP analysis

---

## ⚙ Technologies Used

| Component | Technology / Tool | Purpose |
|-----------|------------------|---------|
| **Data Streaming** | Apache Kafka | Real-time streaming of patient vitals |
| **Data Storage** | Hadoop HDFS (with local fallback) | Distributed storage of health records |
| **Backend Language** | Python 3.10+ | Data processing, ML, and API development |
| **Machine Learning** | Scikit-learn | Diabetes risk prediction model |
| **API Framework** | FastAPI | RESTful API for model predictions |
| **Data Visualization** | Streamlit | Interactive real-time dashboard |
| **Model Explainability** | SHAP | Feature importance and prediction explanations |
| **Data Format** | Parquet | Efficient columnar storage |
| **Containerization** | Docker + Docker Compose | Easy deployment of Kafka, Zookeeper, and HDFS |
| **Dataset** | Pima Indians Diabetes Dataset | Real-world medical dataset for training |

---

## 🧩 System Architecture

### Flow of Data:

**1. Producer.py** (`kafka_producer/producer_vitals.py`)
- Generates realistic patient vitals (heart rate, SpO2, blood pressure, respiratory rate)
- Sends each vitals record as a Kafka message to the topic `vitals`
- Simulates continuous patient monitoring

**2. Kafka Broker**
- Acts as a real-time message queue
- Streams data between producer and consumer with low latency
- Ensures fault-tolerant data delivery

**3. Consumer.py** (`kafka_consumer/consumer_to_hdfs.py`)
- Subscribes to the `vitals` topic
- Consumes incoming patient vitals in real-time
- Implements **time-based flush** (every 5 seconds) for near-real-time updates
- Attempts to write to HDFS; falls back to local Parquet files if HDFS unavailable
- Stores data in `data/vitals_data/` directory

**4. Model Server** (`model_server/app.py`)
- FastAPI-based prediction service running on port **8000**
- Loads pre-trained diabetes prediction model (Random Forest)
- Provides `/predict` endpoint for risk assessment
- Returns probability scores and risk classification

**5. Dashboard** (`dashboard/streamlit_app.py`)
- Streamlit web application running on port **8502**
- **Real-time vitals monitoring**: displays latest patient metrics
- **Historical trend analysis**: shows recent vitals history
- **Interactive prediction interface**: allows manual diabetes risk assessment
- **SHAP explanations**: visualizes feature importance for predictions
- **Auto-refresh**: updates every 5 seconds to show live data

**6. Hadoop HDFS** (Optional)
- NameNode (port 9870): Manages file system metadata
- DataNode: Stores actual data blocks
- WebHDFS API: Allows HTTP-based file operations

---

## 📊 Output

### 1. Real-Time Dashboard (`http://localhost:8502`)
The dashboard displays:

🔴 **Critical Vitals** → Highlighted in red for immediate attention  
🟡 **Warning Range** → Yellow indicators for borderline values  
🟢 **Normal Range** → Green for healthy vitals  
🔵 **Historical Trends** → Table showing recent patient data

### 2. Diabetes Risk Prediction
- **Low Risk**: 0-40% probability (Green)
- **Moderate Risk**: 40-70% probability (Yellow)
- **High Risk**: 70-100% probability (Red)

### 3. SHAP Feature Importance
- Visual breakdown of which factors contribute most to diabetes risk
- Bar charts showing positive/negative impact of each feature

---

## 🧰 How to Run

### Prerequisites
```bash
# Ensure Docker Desktop is installed and running
# Python 3.10+ installed
# At least 4GB RAM available
```

### Step 1: Start Kafka and HDFS
```bash
# Start all infrastructure services
docker-compose up -d

# Verify services are running
docker ps

# Create Kafka topic
docker exec kafka kafka-topics --create --bootstrap-server localhost:9092 --topic vitals --partitions 1 --replication-factor 1 --if-not-exists
```

### Step 2: Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate environment
.\venv\Scripts\Activate.ps1  # Windows PowerShell
source venv/bin/activate      # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Start Producer (Terminal 1)
```bash
python kafka_producer/producer_vitals.py
```
*Output: Continuous stream of patient vitals being published*

### Step 4: Start Consumer (Terminal 2)
```bash
# Set flush interval (optional, default is 5 seconds)
$env:BATCH_FLUSH_SECS="5"  # Windows PowerShell
export BATCH_FLUSH_SECS=5  # Linux/Mac

python kafka_consumer/consumer_to_hdfs.py
```
*Output: Parquet files created every 5 seconds in `data/vitals_data/`*

### Step 5: Start Model Server (Terminal 3)
```bash
uvicorn model_server.app:app --reload --port 8000
```
*API available at: `http://localhost:8000`*

### Step 6: Start Dashboard (Terminal 4)
```bash
streamlit run dashboard/streamlit_app.py --server.port 8502
```
*Dashboard available at: `http://localhost:8502`*

### Step 7: Open Dashboard in Browser
Navigate to: **http://localhost:8502**

---

## 📁 Project Structure

```
healthcare-pipeline/
├── config.py                      # Centralized configuration
├── docker-compose.yml             # Infrastructure services
├── requirements.txt               # Python dependencies
├── hadoop.env                     # Hadoop environment variables
├── HADOOP_SETUP.md               # HDFS setup guide
│
├── kafka_producer/
│   └── producer_vitals.py        # Generates and streams patient vitals
│
├── kafka_consumer/
│   └── consumer_to_hdfs.py       # Consumes data with time-based flush
│
├── dashboard/
│   └── streamlit_app.py          # Interactive monitoring dashboard
│
├── model_server/
│   └── app.py                    # FastAPI prediction service
│
├── model_training/
│   ├── train_model.py            # Model training script
│   └── pima_training.ipynb       # Jupyter notebook for experimentation
│
├── models/
│   ├── model.joblib              # Trained Random Forest model
│   ├── scaler.joblib             # Feature scaler
│   └── shap_explainer.joblib     # SHAP explainer for interpretability
│
├── data/
│   ├── pima.csv                  # Training dataset (Pima Indians Diabetes)
│   └── vitals_data/              # Real-time vitals stored as Parquet files
│
├── connect/
│   └── hdfs-sink-config.json     # Kafka Connect HDFS configuration
│
└── logs/
    └── producer.err              # Error logs
```

---

## 🧩 Project Features

✅ **Real-time data ingestion** with Apache Kafka  
✅ **Time-based batch flushing** for near-real-time updates (5-second intervals)  
✅ **HDFS integration** with intelligent local fallback  
✅ **Machine Learning predictions** with 85%+ accuracy  
✅ **Explainable AI** using SHAP values  
✅ **Interactive dashboard** with auto-refresh  
✅ **Responsive UI** showing vitals metrics and trends  
✅ **RESTful API** for integration with other systems  
✅ **Modular architecture** with independent components  
✅ **Works on Windows** without complex Hadoop setup

---

## 🔌 API Documentation

### Health Check Endpoint
```http
GET http://localhost:8000/health
```
**Response:**
```json
{
  "status": "healthy"
}
```

### Prediction Endpoint
```http
POST http://localhost:8000/predict
Content-Type: application/json
```
**Request Body:**
```json
{
  "pregnancies": 2,
  "glucose": 138,
  "blood_pressure": 62,
  "skin_thickness": 35,
  "insulin": 0,
  "bmi": 33.6,
  "diabetes_pedigree_function": 0.127,
  "age": 47
}
```
**Response:**
```json
{
  "prediction": 1,
  "probability": 0.73,
  "risk_level": "High",
  "message": "High diabetes risk detected"
}
```

---

## 📈 Dashboard Features

### 1. **Real-Time Vitals Monitoring**
- ❤️ Heart Rate (50-140 bpm)
- 🫁 SpO2 (85-100%)
- 🩸 Systolic Blood Pressure (90-180 mmHg)
- 💉 Diastolic Blood Pressure (60-110 mmHg)
- 🌬️ Respiratory Rate (10-30 breaths/min)

### 2. **Patient Information Display**
- Patient ID
- Last update timestamp
- Data freshness indicator

### 3. **Historical Data Table**
- Last 20 vital readings
- Sorted by most recent first
- Auto-refreshes every 5 seconds

### 4. **Diabetes Risk Prediction Interface**
- Manual input form for patient details
- Instant risk calculation
- Confidence score display
- Feature importance visualization

### 5. **SHAP Explainability**
- Bar chart of feature impacts
- Positive/negative contribution indicators
- Detailed breakdown of prediction factors

---

## ⚡ Configuration

### Environment Variables (`.env`)
```env
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=vitals

# HDFS Configuration
HDFS_URL=http://localhost:9870
HDFS_USER=root
HDFS_DIR=/data/vitals/

# Consumer Configuration
BATCH_SIZE=200
BATCH_FLUSH_SECS=5

# Model Paths
MODEL_PATH=models/model.joblib
SCALER_PATH=models/scaler.joblib
```

### Adjusting Refresh Intervals
```bash
# Consumer flush interval (seconds)
$env:BATCH_FLUSH_SECS="3"  # Faster updates

# Dashboard auto-refresh
# Adjust via sidebar slider (1-30 seconds)
```

---

## 🚀 Future Enhancements

🔮 **Replace simulated vitals** with real IoT medical device integration  
🔮 **Multi-disease prediction** (heart disease, hypertension, etc.)  
🔮 **Anomaly detection** for critical vitals threshold breaches  
🔮 **Alert system** via SMS/Email for emergency situations  
🔮 **Spark Streaming** for distributed data processing  
🔮 **Time-series forecasting** for predictive analytics  
🔮 **Mobile app** for remote patient monitoring  
🔮 **Docker Kubernetes** deployment for scalability  
🔮 **Real Hadoop HDFS cluster** instead of local fallback  
🔮 **Model retraining pipeline** with MLflow tracking

---

## 🎓 Technical Highlights

- **Low Latency**: 5-second end-to-end data pipeline (producer → consumer → dashboard)
- **Fault Tolerance**: Automatic HDFS fallback ensures zero data loss
- **Scalability**: Kafka enables horizontal scaling for multiple producers/consumers
- **Modularity**: Independent microservices for easy maintenance
- **Explainability**: SHAP ensures transparent ML predictions
- **Production-Ready**: FastAPI with async support and proper error handling

---

## 🧑‍💻 Developed By

**Name**: Sumit  
**Institution**: [Your College Name]  
**Department**: Computer Science & Engineering  
**Project Type**: Healthcare Analytics & Big Data  
**Year**: 2025  
**GitHub**: [@sumitsr27](https://github.com/sumitsr27)  
**Repository**: [Diabeties-diagonosis-monitor](https://github.com/sumitsr27/Diabeties-diagonosis-monitor)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Pima Indians Diabetes Dataset** from UCI Machine Learning Repository
- **Apache Kafka** community for excellent streaming platform
- **Streamlit** for rapid dashboard development
- **SHAP** library for interpretable ML

---

## 📞 Support

For issues or questions:
- Open an issue on [GitHub](https://github.com/sumitsr27/Diabeties-diagonosis-monitor/issues)
- Email: [your-email@example.com]

---

**⭐ If you find this project useful, please star the repository!**
