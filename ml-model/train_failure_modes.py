"""
Multiclass Failure Mode Prediction Model
Trains to predict specific failure modes (0-5) instead of just binary classification
"""

import os
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(os.path.dirname(BASE_DIR), "data", "NVMe_Drive_Failure_Dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "nvme_failure_mode_model.pkl")
ENCODERS_PATH = os.path.join(BASE_DIR, "feature_encoders.pkl")
COLUMNS_PATH = os.path.join(BASE_DIR, "feature_columns.pkl")

# Failure mode descriptions
FAILURE_MODE_DESCRIPTIONS = {
    0: "Healthy - No abnormal metrics, no error patterns detected",
    1: "Wear-Out Failure - High TBW or life used; flash nearing end-of-life",
    2: "Thermal Failure - Consistently high temperature (>70°C) causing error spikes",
    3: "Power-Related Failure - Multiple unsafe shutdowns leading to corruption or CRC errors",
    4: "Controller/Firmware Failure - Issues tied to firmware versions or controller instability",
    5: "Rapid Error Accumulation - High error rate in early usage (<3000 hours), manufacturing defect"
}

LEAKAGE_COLS = ["Drive_ID", "Failure_Flag"]


def load_and_prepare_data():
    """Load and prepare data for multiclass training."""
    print("🔍 Loading NVMe Drive Failure Dataset...")
    
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")
    
    df = pd.read_csv(DATA_PATH)
    print(f"✅ Loaded {len(df):,} rows × {len(df.columns)} columns")
    
    # Analyze class distribution
    print("\n📊 Failure Mode Distribution:")
    mode_counts = df['Failure_Mode'].value_counts().sort_index()
    for mode, count in mode_counts.items():
        pct = (count / len(df)) * 100
        desc = FAILURE_MODE_DESCRIPTIONS[mode]
        print(f"  Mode {mode}: {count:,} drives ({pct:.1f}%) - {desc}")
    
    return df


def prepare_features_and_target(df):
    """Prepare features and target for training."""
    print("\n🔧 Preparing Features and Target...")
    
    # Target is Failure_Mode (0-5)
    y = df['Failure_Mode']
    
    # Drop leakage columns and target
    cols_to_drop = [c for c in LEAKAGE_COLS if c in df.columns] + ['Failure_Mode']
    X = df.drop(columns=cols_to_drop)
    
    feature_cols = X.columns.tolist()
    print(f"📋 Features: {feature_cols}")
    print(f"🎯 Target classes: {sorted(y.unique())}")
    
    return X, y, feature_cols


def encode_categorical_features(X_train, X_test, feature_cols):
    """One-hot encode categorical features."""
    print("\n🔤 Encoding Categorical Features...")
    
    cat_cols = X_train.select_dtypes(include=['object', 'category']).columns.tolist()
    
    if cat_cols:
        X_train_encoded = pd.get_dummies(X_train, columns=cat_cols, drop_first=False)
        X_test_encoded = pd.get_dummies(X_test, columns=cat_cols, drop_first=False)
        
        # Align columns
        X_test_encoded = X_test_encoded.reindex(columns=X_train_encoded.columns, fill_value=0)
        
        final_features = X_train_encoded.columns.tolist()
        print(f"✅ Encoded {len(cat_cols)} categorical features")
        print(f"📊 Total features after encoding: {len(final_features)}")
        
        return X_train_encoded, X_test_encoded, final_features
    else:
        return X_train, X_test, feature_cols


def train_multiclass_model(X_train, X_test, y_train, y_test, feature_cols):
    """Train Random Forest for multiclass failure mode prediction."""
    print("\n🤖 Training Random Forest Classifier (Multiclass)...")
    
    # Train with class weights for imbalanced data
    clf = RandomForestClassifier(
        n_estimators=150,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        class_weight='balanced',
        n_jobs=1
    )
    
    clf.fit(X_train, y_train)
    print("✅ Training complete")
    
    # Evaluate
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n📈 Model Performance:")
    print(f"Accuracy: {accuracy:.4f} ({accuracy*100:.1f}%)")
    
    print("\n📋 Classification Report:")
    print(classification_report(
        y_test, y_pred,
        target_names=[f"Mode {i}: {FAILURE_MODE_DESCRIPTIONS[i][:30]}" for i in range(6)]
    ))
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': clf.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n🔍 Top 15 Most Important Features:")
    for idx, row in feature_importance.head(15).iterrows():
        print(f"  {row['feature']:<30} {row['importance']:.4f}")
    
    return clf, feature_importance


def save_model_artifacts(clf, feature_cols):
    """Save trained model and feature information."""
    print("\n💾 Saving Model Artifacts...")
    
    joblib.dump(clf, MODEL_PATH)
    joblib.dump(feature_cols, COLUMNS_PATH)
    joblib.dump({
        'descriptions': FAILURE_MODE_DESCRIPTIONS,
        'leakage_cols': LEAKAGE_COLS
    }, ENCODERS_PATH)
    
    print(f"✅ Model saved: {MODEL_PATH}")
    print(f"✅ Features saved: {COLUMNS_PATH}")


def visualize_confusion_matrix(clf, X_test, y_test):
    """Create confusion matrix visualization."""
    print("\n📊 Creating Confusion Matrix...")
    
    y_pred = clf.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=[f"Mode {i}" for i in range(6)],
        yticklabels=[f"Mode {i}" for i in range(6)]
    )
    plt.title('Confusion Matrix - Failure Mode Prediction')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.tight_layout()
    plt.savefig(os.path.join(BASE_DIR, 'confusion_matrix.png'), dpi=300)
    print("✅ Saved as 'confusion_matrix.png'")


def main():
    """Main training pipeline."""
    print("=" * 60)
    print("NVMe MULTICLASS FAILURE MODE PREDICTION MODEL")
    print("=" * 60)
    
    # Load data
    df = load_and_prepare_data()
    
    # Prepare features and target
    X, y, feature_cols = prepare_features_and_target(df)
    
    # Split data
    print("\n📍 Splitting Data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Training: {len(X_train)} samples")
    print(f"Testing: {len(X_test)} samples")
    
    # Encode categorical features
    X_train_enc, X_test_enc, final_features = encode_categorical_features(
        X_train, X_test, feature_cols
    )
    
    # Train model
    clf, feature_importance = train_multiclass_model(
        X_train_enc, X_test_enc, y_train, y_test, final_features
    )
    
    # Save artifacts
    save_model_artifacts(clf, final_features)
    
    # Visualize
    visualize_confusion_matrix(clf, X_test_enc, y_test)
    
    print("\n" + "=" * 60)
    print("✅ TRAINING COMPLETE")
    print("=" * 60)
    print("\n🎯 Model can now predict all 6 failure modes:")
    for mode, desc in FAILURE_MODE_DESCRIPTIONS.items():
        print(f"   {mode}: {desc}")


if __name__ == "__main__":
    main()
