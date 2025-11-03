from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
import joblib
import numpy as np
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'model.joblib')
SCALER_PATH = os.path.join(BASE_DIR, 'models', 'scaler.joblib')

app = FastAPI(title="Diabetes Risk Prediction API")

# Load model and scaler
try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    raise

class VitalsRecord(BaseModel):
    pregnancies: int
    glucose: float
    blood_pressure: float
    skin_thickness: float
    insulin: float
    bmi: float
    diabetes_pedigree_function: float
    age: int

    @validator('pregnancies')
    def validate_pregnancies(cls, v):
        if v < 0:
            raise ValueError('Pregnancies must be non-negative')
        return v

    @validator('glucose', 'blood_pressure', 'skin_thickness', 'insulin', 'bmi')
    def validate_measurements(cls, v):
        if v < 0:
            raise ValueError('Measurements must be non-negative')
        return v

    @validator('age')
    def validate_age(cls, v):
        if v < 0 or v > 120:
            raise ValueError('Age must be between 0 and 120')
        return v

@app.post("/predict")
async def predict(record: VitalsRecord):
    try:
        # Convert input to array
        features = np.array([[
            record.pregnancies,
            record.glucose,
            record.blood_pressure,
            record.skin_thickness,
            record.insulin,
            record.bmi,
            record.diabetes_pedigree_function,
            record.age
        ]])
        
        # Scale features
        features_scaled = scaler.transform(features)
        
        # Make prediction
        prediction = model.predict(features_scaled)[0]
        probability = model.predict_proba(features_scaled)[0][1]
        
        return {
            "risk": "High" if prediction == 1 else "Low",
            "probability": float(probability),
            "risk_score": int(prediction)
        }
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}