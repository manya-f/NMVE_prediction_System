"""
Single Drive Predictor - Multiclass Failure Mode Prediction
Predicts specific failure modes (0-5) for a single drive
"""

import os
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import joblib
from typing import Dict, Tuple

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "nvme_failure_mode_model.pkl")
COLUMNS_PATH = os.path.join(BASE_DIR, "feature_columns.pkl")
ENCODERS_PATH = os.path.join(BASE_DIR, "feature_encoders.pkl")

# Failure mode labels and descriptions
FAILURE_MODE_DESCRIPTIONS = {
    0: "Healthy",
    1: "Wear-Out Failure",
    2: "Thermal Failure",
    3: "Power-Related Failure",
    4: "Controller/Firmware Failure",
    5: "Rapid Error Accumulation"
}

FAILURE_MODE_DETAILS = {
    0: {
        "description": "No abnormal metrics, no error patterns detected",
        "risk_level": "LOW",
        "risk_color": "green",
        "recommendation": "✅ Drive is healthy. Continue monitoring SMART metrics."
    },
    1: {
        "description": "High TBW or percent life used; flash nearing end-of-life",
        "risk_level": "MEDIUM",
        "risk_color": "yellow",
        "recommendation": "⚠️ Drive is aging. Schedule replacement within 3-6 months. Data is safe but monitor closely."
    },
    2: {
        "description": "Consistently high temperature (>70°C) causing error spikes",
        "risk_level": "HIGH",
        "risk_color": "red",
        "recommendation": "🔴 Critical thermal issue. Improve cooling immediately. Risk of imminent failure."
    },
    3: {
        "description": "Multiple unsafe shutdowns leading to corruption or CRC errors",
        "risk_level": "HIGH",
        "risk_color": "red",
        "recommendation": "🔴 Power stability issue. Check PSU and connections. Back up critical data."
    },
    4: {
        "description": "Issues tied to firmware versions or controller instability",
        "risk_level": "MEDIUM",
        "risk_color": "orange",
        "recommendation": "⚠️ Controller/Firmware issue. Consider firmware update or drive replacement."
    },
    5: {
        "description": "High error rate in early usage (<3000 hours), likely manufacturing defect",
        "risk_level": "HIGH",
        "risk_color": "red",
        "recommendation": "🔴 Manufacturing defect suspected. RMA the drive or replace under warranty."
    }
}

LEAKAGE_COLS = ["Drive_ID", "Failure_Mode", "Failure_Flag", "SMART_Warning_Flag"]


def predict_single_drive(drive_data: Dict) -> Dict:
    """
    Predict failure mode for a single drive.
    
    Parameters:
    -----------
    drive_data : dict
        Dictionary with SMART metrics
    
    Returns:
    --------
    dict with prediction, failure mode, and detailed analysis
    """
    if not os.path.exists(MODEL_PATH) or not os.path.exists(COLUMNS_PATH):
        raise FileNotFoundError("ML model files not found. Run train_failure_modes.py first.")
    
    # Load model and features
    clf = joblib.load(MODEL_PATH)
    feature_columns = joblib.load(COLUMNS_PATH)
    
    # Convert to DataFrame
    df = pd.DataFrame([drive_data])
    
    # Drop leakage columns
    cols_to_drop = [c for c in LEAKAGE_COLS if c in df.columns]
    if cols_to_drop:
        df.drop(columns=cols_to_drop, inplace=True)
    
    # One-hot encode categorical columns
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    if cat_cols:
        df = pd.get_dummies(df, columns=cat_cols, drop_first=False)
    
    # Align to training schema
    df = df.reindex(columns=feature_columns, fill_value=0)
    
    # Make prediction
    pred_mode = int(clf.predict(df)[0])
    pred_proba = clf.predict_proba(df)[0]  # Probabilities for each mode
    
    # Get confidence for predicted mode
    confidence = float(pred_proba[pred_mode])
    
    # Collect all mode probabilities
    mode_probabilities = {i: float(pred_proba[i]) for i in range(6)}
    
    # Analyze SMART metrics for specific patterns
    warnings_list = analyze_smart_metrics(drive_data, pred_mode)
    
    details = FAILURE_MODE_DETAILS[pred_mode]
    
    return {
        "failure_mode": pred_mode,
        "failure_mode_label": FAILURE_MODE_DESCRIPTIONS[pred_mode],
        "failure_mode_description": FAILURE_MODE_DETAILS[pred_mode]["description"],
        "confidence": round(confidence, 4),
        "confidence_percent": round(confidence * 100, 1),
        "risk_level": details["risk_level"],
        "risk_color": details["risk_color"],
        "recommendation": details["recommendation"],
        "warnings": warnings_list,
        "mode_probabilities": {
            i: {
                "mode": i,
                "label": FAILURE_MODE_DESCRIPTIONS[i],
                "probability": round(mode_probabilities[i], 4),
                "percentage": round(mode_probabilities[i] * 100, 1)
            }
            for i in range(6)
        }
    }


def analyze_smart_metrics(drive_data: Dict, predicted_mode: int) -> list:
    """Analyze SMART metrics and generate warnings based on predicted failure mode."""
    warnings = []
    
    # Temperature warnings
    temp = drive_data.get('Temperature_C', 0)
    if temp > 70:
        warnings.append(f"CRITICAL: Temperature {temp}°C (threshold: 70°C) - Thermal stress detected")
    elif temp > 60:
        warnings.append(f"WARNING: Temperature {temp}°C is elevated")
    
    # Media errors
    media_errors = drive_data.get('Media_Errors', 0)
    if media_errors > 20:
        warnings.append(f"CRITICAL: Media errors {media_errors} are very high")
    elif media_errors > 10:
        warnings.append(f"WARNING: Media errors {media_errors} indicate potential issues")
    
    # Unsafe shutdowns
    unsafe_shutdowns = drive_data.get('Unsafe_Shutdowns', 0)
    if unsafe_shutdowns > 10:
        warnings.append(f"CRITICAL: {unsafe_shutdowns} unsafe shutdowns detected - Power stability issue")
    elif unsafe_shutdowns > 5:
        warnings.append(f"WARNING: {unsafe_shutdowns} unsafe shutdowns suggest power problems")
    
    # Life used
    life_used = drive_data.get('Percent_Life_Used', 0)
    if life_used > 90:
        warnings.append(f"CRITICAL: Life used {life_used}% - Drive near end-of-life")
    elif life_used > 80:
        warnings.append(f"WARNING: Life used {life_used}% - Approaching end-of-life")
    
    # CRC errors (if provided)
    crc_errors = drive_data.get('CRC_Errors', 0)
    if crc_errors > 5:
        warnings.append(f"WARNING: CRC errors {crc_errors} - Power integrity issues possible")
    
    # Power on hours check for early-life failure
    power_hours = drive_data.get('Power_On_Hours', 0)
    if power_hours < 3000 and media_errors > 20:
        warnings.append(f"CRITICAL: High errors ({media_errors}) detected early ({power_hours} hours) - Possible manufacturing defect")
    
    # TBW analysis for wear-out
    tbw = drive_data.get('Total_TBW_TB', 0)
    if tbw > 300:
        warnings.append(f"WARNING: Total TBW {tbw}TB is high - Heavy usage detected")
    
    return warnings


if __name__ == "__main__":
    # Test with different failure modes
    
    print("Test 1: Healthy Drive")
    healthy_drive = {
        "Vendor": "Samsung",
        "Model": "980 Pro",
        "Firmware_Version": "1.0",
        "Temperature_C": 40.0,
        "Power_On_Hours": 5000,
        "Total_TBW_TB": 50.0,
        "Total_TBR_TB": 45.0,
        "Unsafe_Shutdowns": 1,
        "Media_Errors": 0,
        "Percent_Life_Used": 20.0,
        "Available_Spare": 98.0,
        "CRC_Errors": 0
    }
    result = predict_single_drive(healthy_drive)
    print(f"Mode {result['failure_mode']}: {result['failure_mode_label']} (Confidence: {result['confidence_percent']}%)\n")
    
    print("Test 2: Thermal Failure")
    thermal_drive = {
        "Vendor": "Crucial",
        "Model": "P5",
        "Firmware_Version": "2.0",
        "Temperature_C": 80.0,
        "Power_On_Hours": 10000,
        "Total_TBW_TB": 120.0,
        "Total_TBR_TB": 100.0,
        "Unsafe_Shutdowns": 2,
        "Media_Errors": 15,
        "Percent_Life_Used": 50.0,
        "Available_Spare": 85.0,
        "CRC_Errors": 2
    }
    result = predict_single_drive(thermal_drive)
    print(f"Mode {result['failure_mode']}: {result['failure_mode_label']} (Confidence: {result['confidence_percent']}%)\n")
    
    print("Test 3: Wear-Out Failure")
    wearout_drive = {
        "Vendor": "Samsung",
        "Model": "970 EVO",
        "Firmware_Version": "3.0",
        "Temperature_C": 45.0,
        "Power_On_Hours": 50000,
        "Total_TBW_TB": 450.0,
        "Total_TBR_TB": 400.0,
        "Unsafe_Shutdowns": 1,
        "Media_Errors": 5,
        "Percent_Life_Used": 95.0,
        "Available_Spare": 2.0,
        "CRC_Errors": 0
    }
    result = predict_single_drive(wearout_drive)
    print(f"Mode {result['failure_mode']}: {result['failure_mode_label']} (Confidence: {result['confidence_percent']}%)\n")

