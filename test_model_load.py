import joblib
import pandas as pd
import os

BASE_DIR = r"c:\Users\Sumit\Desktop\healthcare-pipeline"
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'model.joblib')
SCALER_PATH = os.path.join(BASE_DIR, 'models', 'scaler.joblib')
DATA_PATH = os.path.join(BASE_DIR, 'data', 'pima.csv')

print('MODEL_PATH =', MODEL_PATH)
print('SCALER_PATH =', SCALER_PATH)
print('DATA_PATH =', DATA_PATH)

# Load files
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

# Read first non-header row from data
cols = ["Pregnancies", "Glucose", "BloodPressure", "SkinThickness", "Insulin",
        "BMI", "DiabetesPedigreeFunction", "Age", "Outcome"]

df = pd.read_csv(DATA_PATH, names=cols, skiprows=[0])
# convert to numeric
for c in df.columns:
    df[c] = pd.to_numeric(df[c])

sample = df.drop('Outcome', axis=1).iloc[0:1]
print('Sample input:\n', sample)

X_scaled = scaler.transform(sample)
pred = model.predict(X_scaled)[0]
prob = model.predict_proba(X_scaled)[0][1] if hasattr(model, 'predict_proba') else None

print('Prediction:', pred)
print('Probability:', prob)
