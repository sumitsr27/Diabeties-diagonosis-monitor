# 🏗️ System Architecture - Healthcare Monitoring Pipeline

## 📐 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         HEALTHCARE MONITORING SYSTEM                      │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Producer   │────────▶│    Kafka     │────────▶│   Consumer   │
│ (Vitals Gen) │  Pub    │   Broker     │  Sub    │ (Storage)    │
└──────────────┘         └──────────────┘         └──────────────┘
       │                        │                          │
       │                        │                          ▼
       │                        │                  ┌──────────────┐
       │                        │                  │  Parquet     │
       │                        │                  │  Files       │
       │                        │                  └──────────────┘
       │                        │                          │
       │                        │                          │
       ▼                        ▼                          ▼
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│  Zookeeper   │         │    HDFS      │         │  Dashboard   │
│ (Coordination)│         │ (Optional)   │         │ (Streamlit)  │
└──────────────┘         └──────────────┘         └──────────────┘
                                                           │
                                                           │
                                                           ▼
                                                   ┌──────────────┐
                                                   │ Model Server │
                                                   │  (FastAPI)   │
                                                   └──────────────┘
                                                           │
                                                           ▼
                                                   ┌──────────────┐
                                                   │  ML Models   │
                                                   │ (Joblib)     │
                                                   └──────────────┘
```

---

## 🔄 Detailed Data Flow

### Stage 1: Data Generation & Ingestion
```
┌──────────────────────────────────────────────────────────────┐
│ PRODUCER (producer_vitals.py)                                │
├──────────────────────────────────────────────────────────────┤
│ 1. Generate random patient vitals every 0.5 seconds          │
│    - Patient ID (UUID)                                        │
│    - Timestamp (Unix epoch)                                   │
│    - Heart Rate (50-140 bpm)                                  │
│    - SpO2 (85-100%)                                           │
│    - Systolic BP (90-180 mmHg)                                │
│    - Diastolic BP (60-110 mmHg)                               │
│    - Respiratory Rate (10-30 breaths/min)                     │
│                                                               │
│ 2. Serialize to JSON                                          │
│ 3. Publish to Kafka topic "vitals"                           │
└──────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│ KAFKA BROKER (Port 9092)                                      │
├──────────────────────────────────────────────────────────────┤
│ - Topic: "vitals"                                             │
│ - Partitions: 1                                               │
│ - Replication: 1                                              │
│ - Retention: 7 days                                           │
│ - Message Format: JSON                                        │
└──────────────────────────────────────────────────────────────┘
```

### Stage 2: Data Consumption & Storage
```
┌──────────────────────────────────────────────────────────────┐
│ CONSUMER (consumer_to_hdfs.py)                               │
├──────────────────────────────────────────────────────────────┤
│ 1. Subscribe to "vitals" topic                                │
│ 2. Consumer Group: "vitals_consumer_group"                    │
│ 3. Deserialize JSON messages                                  │
│ 4. Buffer messages in memory                                  │
│                                                               │
│ FLUSH CONDITIONS:                                             │
│ ┌─────────────────────────────────────────┐                  │
│ │ A) Batch Size: 200 records  OR          │                  │
│ │ B) Time-based: 5 seconds elapsed        │                  │
│ └─────────────────────────────────────────┘                  │
│                                                               │
│ 5. Convert buffer to Pandas DataFrame                         │
│ 6. Write to Parquet (compressed columnar format)             │
│                                                               │
│ STORAGE STRATEGY:                                             │
│ ┌─────────────────────────────────────────┐                  │
│ │ Try: HDFS WebHDFS API                   │                  │
│ │      └─ Path: /data/vitals/             │                  │
│ │ Catch: NameResolutionError              │                  │
│ │      └─ Fallback: Local Directory       │                  │
│ │         Path: data/vitals_data/         │                  │
│ └─────────────────────────────────────────┘                  │
│                                                               │
│ 7. File naming: vitals_{timestamp}.parquet                   │
└──────────────────────────────────────────────────────────────┘
```

### Stage 3: Visualization & Analysis
```
┌──────────────────────────────────────────────────────────────┐
│ DASHBOARD (streamlit_app.py)                                 │
├──────────────────────────────────────────────────────────────┤
│ AUTO-REFRESH LOOP (every 5 seconds):                         │
│                                                               │
│ 1. Scan data/vitals_data/ directory                          │
│ 2. Sort files by timestamp (descending)                      │
│ 3. Read latest 2 Parquet files                               │
│ 4. Concatenate into single DataFrame                         │
│ 5. Sort by timestamp (newest first)                          │
│                                                               │
│ DISPLAY COMPONENTS:                                           │
│ ┌─────────────────────────────────────────┐                  │
│ │ Top Row: 5 Metric Cards                 │                  │
│ │ - Heart Rate | SpO2 | Systolic |        │                  │
│ │   Diastolic | Respiratory Rate          │                  │
│ ├─────────────────────────────────────────┤                  │
│ │ Info Banner: Patient ID + Timestamp     │                  │
│ ├─────────────────────────────────────────┤                  │
│ │ Data Table: Recent 20 Records           │                  │
│ ├─────────────────────────────────────────┤                  │
│ │ Prediction Form:                         │                  │
│ │ - Manual input fields                    │                  │
│ │ - "Predict Risk" button                  │                  │
│ │ - Result display with confidence         │                  │
│ ├─────────────────────────────────────────┤                  │
│ │ SHAP Explanation Chart                   │                  │
│ │ - Feature importance bars                │                  │
│ │ - Positive/negative impacts              │                  │
│ └─────────────────────────────────────────┘                  │
│                                                               │
│ 6. time.sleep(refresh_interval)                              │
│ 7. st.rerun() → Loop back to step 1                          │
└──────────────────────────────────────────────────────────────┘
```

### Stage 4: ML Prediction Service
```
┌──────────────────────────────────────────────────────────────┐
│ MODEL SERVER (app.py - FastAPI)                              │
├──────────────────────────────────────────────────────────────┤
│ INITIALIZATION:                                               │
│ 1. Load model.joblib (Random Forest Classifier)             │
│ 2. Load scaler.joblib (StandardScaler)                      │
│ 3. Load shap_explainer.joblib (TreeExplainer)               │
│                                                               │
│ ENDPOINTS:                                                    │
│ ┌─────────────────────────────────────────┐                  │
│ │ GET /health                              │                  │
│ │ └─ Returns: {"status": "healthy"}       │                  │
│ ├─────────────────────────────────────────┤                  │
│ │ POST /predict                            │                  │
│ │ ├─ Input: Patient data (8 features)     │                  │
│ │ ├─ Validate: Pydantic model              │                  │
│ │ ├─ Scale: StandardScaler transform       │                  │
│ │ ├─ Predict: model.predict_proba()        │                  │
│ │ └─ Return: Risk level + probability      │                  │
│ └─────────────────────────────────────────┘                  │
│                                                               │
│ PREDICTION PIPELINE:                                          │
│ Input → Validation → Scaling → Inference → Response          │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔐 Security & Error Handling

### Fault Tolerance Mechanisms

1. **Kafka Retry Logic**
   - Producer: 5 retries with exponential backoff
   - Consumer: Auto-reconnect on connection loss

2. **HDFS Fallback Strategy**
   ```python
   try:
       write_to_hdfs(data)
   except NameResolutionError:
       write_to_local(data)  # Guaranteed success
   ```

3. **Dashboard Resilience**
   - Graceful handling of missing data files
   - Auto-recovery on refresh
   - Error messages instead of crashes

4. **Model Server Validation**
   - Input schema validation with Pydantic
   - Range checks for all features
   - Exception handling with informative errors

---

## 📊 Performance Characteristics

### Throughput
- **Producer**: 2 messages/second
- **Consumer**: 200 messages/batch OR 5-second intervals
- **Dashboard**: Refresh every 5 seconds
- **End-to-End Latency**: ~5-10 seconds

### Storage Efficiency
- **Format**: Parquet (columnar compression)
- **Compression Ratio**: ~3:1 vs JSON
- **File Size**: ~2-5 KB per batch (200 records)

### Scalability
- **Horizontal Scaling**: Add more producer/consumer instances
- **Kafka Partitions**: Increase for parallel processing
- **Consumer Groups**: Multiple groups for different purposes

---

## 🔄 Component Interaction Matrix

```
┌──────────┬───────┬────────┬──────────┬───────────┬──────┐
│          │ Prod. │ Kafka  │ Consumer │ Dashboard │ API  │
├──────────┼───────┼────────┼──────────┼───────────┼──────┤
│ Producer │   -   │  Pub   │    -     │     -     │  -   │
├──────────┼───────┼────────┼──────────┼───────────┼──────┤
│ Kafka    │  Recv │   -    │   Sub    │     -     │  -   │
├──────────┼───────┼────────┼──────────┼───────────┼──────┤
│ Consumer │   -   │  Poll  │    -     │  Writes   │  -   │
├──────────┼───────┼────────┼──────────┼───────────┼──────┤
│Dashboard │   -   │   -    │  Reads   │     -     │ Calls│
├──────────┼───────┼────────┼──────────┼───────────┼──────┤
│ Model    │   -   │   -    │    -     │  Returns  │  -   │
│ Server   │       │        │          │           │      │
└──────────┴───────┴────────┴──────────┴───────────┴──────┘
```

---

## 🛠️ Technology Stack Details

### Infrastructure Layer
- **Docker**: Containerization platform
- **Docker Compose**: Multi-container orchestration
- **Zookeeper**: Kafka cluster coordination
- **Hadoop HDFS**: Distributed file system (optional)

### Data Layer
- **Apache Kafka**: Event streaming platform
  - Version: 2.5.0 (Confluent Platform 7.4.1)
  - Message Format: JSON
  - Serialization: UTF-8 encoded strings

- **Parquet**: Storage format
  - Engine: PyArrow
  - Compression: Snappy (default)
  - Schema: Inferred from DataFrame

### Application Layer
- **Python 3.10+**: Primary language
- **Kafka-Python**: Kafka client library
- **Confluent-Kafka**: Alternative Kafka client
- **Pandas**: Data manipulation
- **NumPy**: Numerical operations

### ML Layer
- **Scikit-learn**: ML framework
  - Algorithm: Random Forest Classifier
  - Features: 8 (pregnancies, glucose, BP, etc.)
  - Target: Binary (diabetes yes/no)

- **SHAP**: Model explainability
  - Explainer: TreeExplainer
  - Output: Feature importance values

### Web Layer
- **Streamlit**: Dashboard framework
  - Components: Metrics, Tables, Charts, Forms
  - Interaction: Sidebar controls, buttons

- **FastAPI**: API framework
  - Features: Auto-docs, validation, async support
  - Server: Uvicorn (ASGI)

---

## 📈 Monitoring & Observability

### Logs
- **Producer**: Console output with message content
- **Consumer**: INFO-level logs for batch writes
- **Model Server**: Request/response logging
- **Dashboard**: Streamlit runtime logs

### Metrics
- **Kafka**: Offset lag, partition assignments
- **Consumer**: Batch size, flush frequency
- **Dashboard**: Refresh rate, data freshness
- **Model**: Prediction latency, request count

### Health Checks
- **Docker**: Container health status
- **Kafka**: Topic availability
- **HDFS**: NameNode web UI (port 9870)
- **Model Server**: `/health` endpoint

---

**This architecture ensures high availability, fault tolerance, and scalability for real-time healthcare monitoring.**
