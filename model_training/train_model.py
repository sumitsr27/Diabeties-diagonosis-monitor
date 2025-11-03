import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
import joblib
import shap


import os

# Define absolute paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(BASE_DIR, 'data', 'pima.csv')
MODEL_OUT = os.path.join(BASE_DIR, 'models', 'model.joblib')
SCALER_OUT = os.path.join(BASE_DIR, 'models', 'scaler.joblib')

if __name__ == '__main__':
    # Create models directory if it doesn't exist
    os.makedirs(os.path.dirname(MODEL_OUT), exist_ok=True)
    
    # Load and prepare data
    df = pd.read_csv(PATH)
    X = df.drop(columns=['Outcome'])
    y = df['Outcome']

    # Train test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Initialize and train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate model
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]
    print("\nModel Evaluation:")
    print("-" * 20)
    print(classification_report(y_test, preds))
    print('ROC AUC:', roc_auc_score(y_test, probs))

    # Save model
    joblib.dump(model, MODEL_OUT)
    print(f"\n✅ Model saved to {MODEL_OUT}")


    # Create and save SHAP explainer
    print("\nGenerating SHAP explainer...")
    explainer = shap.TreeExplainer(model)
    shap_vals = explainer.shap_values(X_test)
    explainer_path = os.path.join(BASE_DIR, 'models', 'shap_explainer.joblib')
    joblib.dump({'explainer': explainer, 'feature_names': X.columns.tolist()}, explainer_path)
    print(f"✅ SHAP explainer saved to {explainer_path}")