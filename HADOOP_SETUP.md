# Hadoop HDFS Integration Setup Guide

## What's New? 🎉
Your healthcare pipeline now supports **Hadoop HDFS** for distributed storage!

## Architecture Update

**Before:**
```
Kafka Producer → Kafka → Consumer → Local Files (data/vitals_data/)
```

**Now:**
```
Kafka Producer → Kafka → Consumer → HDFS (distributed storage)
                                   ↓ (fallback)
                                   Local Files
```

## Setup Instructions

### 1. Start Docker Desktop
Make sure Docker Desktop is running on your Windows machine.

### 2. Start All Services (Kafka + Hadoop)
```powershell
# Navigate to project directory
cd C:\Users\Sumit\Desktop\healthcare-pipeline

# Stop any existing containers
docker-compose down

# Start Kafka + Hadoop services
docker-compose up -d
```

This will start:
- ✅ Zookeeper (port 2181)
- ✅ Kafka (port 9092)  
- ✅ **Hadoop NameNode** (port 9870, 9000)
- ✅ **Hadoop DataNode** (distributed storage)

### 3. Verify HDFS is Running
```powershell
# Check containers
docker ps

# You should see:
# - zookeeper
# - kafka
# - namenode
# - datanode
```

**Access HDFS Web UI:**
Open browser: http://localhost:9870

### 4. Test HDFS Connection
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run HDFS test script
python test_hdfs.py
```

If successful, you'll see:
```
✓ Connected to HDFS successfully!
✓ Directory /data/vitals/ is ready
✓ Write test successful
✓ Read test successful
✅ HDFS is ready for use!
```

### 5. Start Application Services
```powershell
# Start all services (FastAPI, Streamlit, Producer, Consumer)
python start_services.py
```

## How It Works

### Consumer Behavior
The consumer (`consumer_to_hdfs.py`) now:

1. **First tries HDFS**: Connects to Hadoop and writes data there
2. **Fallback to Local**: If HDFS is unavailable, writes to local files

You'll see in logs:
```
INFO:__main__:Successfully connected to HDFS at http://localhost:9870
INFO:__main__:Wrote 200 records to HDFS: /data/vitals/vitals_1762181352.parquet
```

Or if HDFS is down:
```
WARNING:__main__:HDFS not available, falling back to local storage
INFO:__main__:Wrote 200 records to local: data/vitals_data/vitals_1762181352.parquet
```

## HDFS Features

### Web UI (http://localhost:9870)
- View stored files
- Monitor cluster health
- Check storage usage
- Browse HDFS directories

### Data Storage
- **Location**: `/data/vitals/` in HDFS
- **Format**: Parquet files
- **Distributed**: Data spread across DataNode(s)
- **Fault-tolerant**: Hadoop handles replication

## Troubleshooting

### Docker Not Running
```
Error: open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file
```
**Solution**: Start Docker Desktop application

### HDFS Connection Failed
```
HDFS not available, falling back to local storage
```
**Solution**: 
1. Check containers: `docker ps`
2. Restart: `docker-compose restart namenode`
3. Check logs: `docker logs namenode`

### Port Already in Use
```
Error: port is already allocated
```
**Solution**: Stop conflicting services or change ports in docker-compose.yml

## Configuration

Edit `.env` or `config.py` to customize:
```python
HDFS_URL = 'http://localhost:9870'
HDFS_USER = 'root'
HDFS_DIR = '/data/vitals/'
```

## Benefits of Using HDFS

✅ **Scalability**: Handle petabytes of data  
✅ **Fault Tolerance**: Automatic data replication  
✅ **Distributed**: Parallel processing across nodes  
✅ **Enterprise-ready**: Production-grade storage  
✅ **Flexible**: Easy to add more DataNodes  

## Next Steps

1. ✅ Start Docker Desktop
2. ✅ Run `docker-compose up -d`
3. ✅ Test with `python test_hdfs.py`
4. ✅ Start application with `python start_services.py`
5. ✅ Monitor at http://localhost:9870

---

**Note**: The system will automatically fall back to local storage if HDFS is not available, so your application continues to work seamlessly!
