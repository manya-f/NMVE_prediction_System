import os
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
DATA_PATH = os.path.join(ROOT_DIR, "data", "NVMe_Drive_Failure_Dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")  # Save as model.pkl as requested

# Feature mapping: user names -> CSV column names
FEATURE_MAPPING = {
    'temperature': 'Temperature_C',
    'power_on_hours': 'Power_On_Hours',
    'life_used': 'Percent_Life_Used',
    'error_count': 'Media_Errors',  # Assuming this is what user means
    'unsafe_shutdowns': 'Unsafe_Shutdowns'
}

def main():
    print("Loading dataset...")
    df = pd.read_csv(DATA_PATH)

    # Create target: Failure_Mode == 0 -> 0 (SAFE), > 0 -> 1 (FAIL)
    df['target'] = (df['Failure_Mode'] != 0).astype(int)

    # Select only the 5 features we need
    selected_features = list(FEATURE_MAPPING.values())
    X = df[selected_features]
    y = df['target']

    print(f"Selected features: {selected_features}")
    print(f"Dataset shape: {X.shape}")
    print(f"Target distribution: SAFE={sum(y==0)}, FAIL={sum(y==1)}")

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Train model
    print("Training model...")
    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight='balanced'  # Handle imbalance
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print("Classification Report:")
    print(classification_report(y_test, y_pred))

    # Save model
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    main()