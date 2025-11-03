import streamlit as st
import pandas as pd
import joblib
import numpy as np
import shap
import os
import time

# Load model and scaler (use models/ directory created by training notebook)
MODEL_PATH = "models/model.joblib"
SCALER_PATH = "models/scaler.joblib"
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

st.set_page_config(page_title="Diabetes Risk Prediction Dashboard", layout="wide")
st.title("🩺 Diabetes Patient Monitoring System")

# Add real-time vitals monitoring
st.write("### 📊 Real-time Patient Vitals")
DATA_DIR = "data/vitals_data"

# Auto-refresh settings
auto_refresh = st.sidebar.checkbox("Enable auto-refresh", value=True)
refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 1, 30, 5)

# Create a placeholder for auto-refresh
placeholder = st.empty()

# Get the latest vitals data
try:
    # Force refresh the directory listing
    vitals_files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith('.parquet')], 
                         key=lambda x: int(x.split('_')[1].split('.')[0]),
                         reverse=True)
    if vitals_files:
        # Read and combine the latest 2 parquet files to ensure we have the most recent data
        latest_files = vitals_files[:2]
        latest_data = pd.concat([pd.read_parquet(os.path.join(DATA_DIR, f)) for f in latest_files])
        latest_data = latest_data.sort_values('timestamp', ascending=False)
        
        # Display key metrics from the most recent record
        if not latest_data.empty:
            latest_row = latest_data.iloc[0]
            
            # Show metrics in columns
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("❤️ Heart Rate", f"{latest_row['heart_rate']} bpm")
            with col2:
                st.metric("🫁 SpO2", f"{latest_row['spo2']}%")
            with col3:
                st.metric("🩸 Systolic", f"{latest_row['systolic']} mmHg")
            with col4:
                st.metric("💉 Diastolic", f"{latest_row['diastolic']} mmHg")
            with col5:
                st.metric("🌬️ Resp. Rate", f"{latest_row['respiratory_rate']}/min")
            
            # Show patient ID and timestamp
            last_timestamp = pd.to_datetime(latest_row['timestamp'], unit='s')
            st.info(f"👤 Patient ID: {latest_row['patient_id']} | 🕐 Last updated: {last_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        st.write("### Recent Vitals History")
        st.dataframe(latest_data.head(20), use_container_width=True)
    else:
        st.warning("No vitals data available yet. Waiting for data from Kafka...")
except FileNotFoundError:
    st.warning("Vitals data directory not found. Waiting for consumer to create data...")
except Exception as e:
    st.error(f"Error loading vitals data: {str(e)}")

st.write("### Enter patient details below to predict diabetes risk")

# Refresh controls
col1, col2 = st.columns([1, 3])
with col1:
    if st.button("Refresh vitals"):
        st.rerun()
with col2:
    use_latest = st.checkbox("Prefill form from latest vitals (bp only)", value=True)

# Prepare default values (map latest vitals where possible)
pregnancies_default = 1
glucose_default = 120
bp_default = 70
skin_default = 20
insulin_default = 80
bmi_default = 25.0
dpf_default = 0.5
age_default = 30

try:
    if 'latest_data' in locals() and not latest_data.empty:
        latest_row = latest_data.iloc[-1]
        # Map available vitals to prediction fields where sensible
        # Use systolic as a proxy for blood_pressure
        if use_latest:
            if 'systolic' in latest_row:
                try:
                    bp_default = int(latest_row['systolic'])
                except Exception:
                    bp_default = bp_default
except Exception:
    # keep defaults on any error
    pass

# Input form (values pre-filled from defaults above)
pregnancies = st.number_input("Pregnancies", min_value=0, max_value=20, value=pregnancies_default)
glucose = st.number_input("Glucose Level", min_value=0, max_value=200, value=glucose_default)
bp = st.number_input("Blood Pressure", min_value=0, max_value=300, value=bp_default)
skin = st.number_input("Skin Thickness", min_value=0, max_value=100, value=skin_default)
insulin = st.number_input("Insulin Level", min_value=0, max_value=900, value=insulin_default)
bmi = st.number_input("BMI", min_value=0.0, max_value=70.0, value=bmi_default)
dpf = st.number_input("Diabetes Pedigree Function", min_value=0.0, max_value=3.0, value=dpf_default)
age = st.number_input("Age", min_value=1, max_value=120, value=age_default)

if st.button("Predict Risk"):
    X_input = np.array([[pregnancies, glucose, bp, skin, insulin, bmi, dpf, age]])
    X_scaled = scaler.transform(X_input)
    prediction = model.predict(X_scaled)[0]
    proba = model.predict_proba(X_scaled)[0][1]

    st.subheader("🧠 Prediction Result:")
    st.write(f"**Risk:** {'High' if prediction == 1 else 'Low'}")
    st.write(f"**Confidence:** {proba * 100:.2f}%")

    # SHAP explanation
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_scaled)
        st.write("### 🔍 Feature Importance (SHAP)")
        feature_names = ["Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
                        "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"]
        
        # For binary classification models
        if isinstance(shap_values, list):
            # Use the positive class (class 1) SHAP values
            shap_values = shap_values[1]
        
        # Extract SHAP values for the single prediction
        shap_values = shap_values.flatten() if hasattr(shap_values, 'flatten') else shap_values
        
        # Create DataFrame with feature importance
        feature_importance = pd.DataFrame({
            'Feature': feature_names,
            'SHAP Value': np.abs(shap_values)
        }).sort_values('SHAP Value', ascending=False)
        
        # Display feature importance
        st.bar_chart(data=feature_importance.set_index('Feature'))
        
        # Show detailed breakdown
        st.write("### Detailed Feature Impact")
        for idx, row in feature_importance.iterrows():
            impact = "High positive" if row['SHAP Value'] > 0 else "High negative" if row['SHAP Value'] < 0 else "Neutral"
            st.write(f"- **{row['Feature']}**: Impact = {impact} (SHAP value: {row['SHAP Value']:.4f})")
    except Exception as e:
        st.error(f"Could not generate SHAP explanation: {str(e)}")
        # Fallback to feature importance from the model if available
        if hasattr(model, 'feature_importances_'):
            st.write("### 🔍 Feature Importance (from model)")
            feature_importance = pd.DataFrame({
                'Feature': feature_names,
                'Importance': model.feature_importances_
            }).sort_values('Importance', ascending=False)
            st.bar_chart(data=feature_importance.set_index('Feature'))

# Auto-refresh logic at the bottom
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
