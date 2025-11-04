# 🚀 Quick Start Guide

## One-Command Setup (After Docker is Running)

```bash
# Windows PowerShell
docker-compose up -d; Start-Sleep -Seconds 20; docker exec kafka kafka-topics --create --bootstrap-server localhost:9092 --topic vitals --partitions 1 --replication-factor 1 --if-not-exists; .\venv\Scripts\python.exe kafka_producer\producer_vitals.py
```

## Manual Step-by-Step (Recommended for First Time)

### 1️⃣ Start Infrastructure (1 minute)
```bash
docker-compose up -d
```
Wait 20 seconds for services to initialize.

### 2️⃣ Create Kafka Topic (10 seconds)
```bash
docker exec kafka kafka-topics --create --bootstrap-server localhost:9092 --topic vitals --partitions 1 --replication-factor 1 --if-not-exists
```

### 3️⃣ Activate Virtual Environment (5 seconds)
```bash
.\venv\Scripts\Activate.ps1
```

### 4️⃣ Start Producer (Terminal 1)
```bash
python kafka_producer\producer_vitals.py
```
✅ You should see: `sent {'patient_id': 'xxx', 'timestamp': ..., 'heart_rate': 120, ...}`

### 5️⃣ Start Consumer (Terminal 2)
```bash
$env:BATCH_FLUSH_SECS="5"
python kafka_consumer\consumer_to_hdfs.py
```
✅ You should see: `INFO:__main__:Wrote 58 records to local: data\vitals_data\vitals_xxx.parquet`

### 6️⃣ Start Dashboard (Terminal 3)
```bash
streamlit run dashboard\streamlit_app.py --server.port 8502
```
✅ Browser opens automatically at http://localhost:8502

### 7️⃣ (Optional) Start Model Server (Terminal 4)
```bash
uvicorn model_server.app:app --reload --port 8000
```
✅ API available at http://localhost:8000/docs

---

## ✅ Verify Everything is Working

### Check Docker Containers
```bash
docker ps
```
Expected output: 4 containers (zookeeper, kafka, namenode, datanode) all "Up" and "healthy"

### Check Data Files
```bash
Get-ChildItem data\vitals_data -Filter *.parquet | Sort-Object LastWriteTime -Descending | Select-Object -First 5
```
Expected output: New `.parquet` files with recent timestamps

### Check Dashboard
1. Open http://localhost:8502
2. Verify metrics are updating (watch the timestamp)
3. Toggle "Enable auto-refresh" in sidebar if needed
4. Adjust refresh interval (1-30 seconds)

---

## 🛑 Stop All Services

```bash
# Stop Python processes (Ctrl+C in each terminal)

# Stop Docker containers
docker-compose down

# (Optional) Remove volumes to start fresh
docker-compose down -v
```

---

## 🔧 Troubleshooting

### Problem: Kafka connection refused
**Solution**: 
```bash
docker-compose down
docker-compose up -d
Start-Sleep -Seconds 30
# Then retry producer
```

### Problem: Dashboard shows "No vitals data"
**Solution**: 
- Ensure producer is running (check Terminal 1)
- Ensure consumer is running (check Terminal 2)
- Wait 5-10 seconds for first batch to flush
- Click "Refresh vitals" button in dashboard

### Problem: HDFS errors in consumer logs
**Solution**: This is expected! Consumer automatically falls back to local storage. Ignore these errors.

### Problem: Module not found errors
**Solution**:
```bash
pip install -r requirements.txt
```

---

## 📊 Expected Output Examples

### Producer Output
```
sent {'patient_id': 'abc123', 'timestamp': 1762232176, 'heart_rate': 119, 'spo2': 100, 'systolic': 171, 'diastolic': 110, 'respiratory_rate': 16}
sent {'patient_id': 'def456', 'timestamp': 1762232177, 'heart_rate': 132, 'spo2': 92, 'systolic': 156, 'diastolic': 61, 'respiratory_rate': 12}
```

### Consumer Output
```
INFO:__main__:Successfully connected to HDFS at http://localhost:9870
INFO:kafka.coordinator:Successfully joined group vitals_consumer_group
ERROR:__main__:Failed to write batch to HDFS: ... (Expected - fallback working)
INFO:__main__:Wrote 58 records to local: data\vitals_data\vitals_1762252055.parquet
INFO:__main__:Latest vitals data sample: {'patient_id': 'bdc8a164', 'timestamp': 1762232253, ...}
```

### Dashboard Output
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8502
Network URL: http://192.168.x.x:8502
```

---

## 🎯 What to Demonstrate

1. **Real-time Updates**: Show timestamp changing every 5 seconds
2. **Vitals Metrics**: Point out the 5 metric cards at top
3. **Historical Table**: Show recent 20 records scrolling
4. **Prediction**: Enter values and click "Predict Risk"
5. **SHAP Explanation**: Show feature importance chart
6. **Configuration**: Toggle auto-refresh and adjust interval

---

## 💡 Pro Tips

- **Faster Updates**: Set `$env:BATCH_FLUSH_SECS="2"` for 2-second intervals
- **Clean Start**: Run `docker-compose down -v` to reset all data
- **Multiple Producers**: Run multiple producer terminals for higher data volume
- **API Testing**: Visit http://localhost:8000/docs for interactive Swagger UI
- **Logs**: Check `logs/producer.err` for detailed error messages

---

## 🌐 Access Points

| Service | URL | Port |
|---------|-----|------|
| **Dashboard** | http://localhost:8502 | 8502 |
| **Model API** | http://localhost:8000 | 8000 |
| **API Docs** | http://localhost:8000/docs | 8000 |
| **Kafka** | localhost:9092 | 9092 |
| **HDFS NameNode** | http://localhost:9870 | 9870 |
| **Zookeeper** | localhost:2181 | 2181 |

---

**Need help? Check the main README.md or open an issue on GitHub!**
