# import os
# import sys
# import joblib
# import pandas as pd
# import numpy as np
# from flask import Flask, jsonify, request, render_template
# from flask_cors import CORS

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# MODEL_PATH = os.path.join(BASE_DIR, "models", "model.pkl")

# # Initialize Flask app
# app = Flask(__name__, template_folder="templates", static_folder="static")

# # Enable CORS for all routes
# CORS(app)

# # Additional CORS headers for safety
# @app.after_request
# def after_request(response):
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
#     response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
#     return response


# # Load model
# try:
#     if not os.path.exists(MODEL_PATH):
#         print(f"ERROR: Model not found at {MODEL_PATH}")
#         print(f"Please run: python ml-model/train_simple.py")
#         sys.exit(1)
#     model = joblib.load(MODEL_PATH)
#     print(f"✓ Model loaded successfully from {MODEL_PATH}")
# except Exception as e:
#     print(f"ERROR loading model: {e}")
#     sys.exit(1)


# # Feature definitions
# INPUT_FEATURES = ["temperature", "power_on_hours", "life_used", "unsafe_shutdowns", "media_errors"]
# MODEL_FEATURES = ["Temperature_C", "Power_On_Hours", "Percent_Life_Used", "Unsafe_Shutdowns", "Media_Errors"]

# FAILURE_MODE_LABELS = {
#     "healthy": "✓ Healthy",
#     "wear_out": "⚠ Wear-Out Failure",
#     "thermal": "🔥 Thermal Failure",
#     "power": "⚡ Power-Related Failure",
#     "firmware": "🔧 Controller/Firmware Failure",
#     "early_life": "⛔ Early-Life Failure",
# }


# def validate_request_data(data):
#     """Validate and clean input data."""
#     if not isinstance(data, dict):
#         raise ValueError("Invalid JSON payload")

#     cleaned = {}
#     for key in INPUT_FEATURES:
#         if key == "media_errors":
#             value = data.get("media_errors", data.get("error_count"))
#             if value is None:
#                 raise ValueError("Missing required field: media_errors or error_count")
#         else:
#             if key not in data:
#                 raise ValueError(f"Missing required field: {key}")
#             value = data[key]

#         if value is None or value == "":
#             raise ValueError(f"Field '{key}' cannot be empty")

#         try:
#             cleaned[key] = float(value)
#         except (TypeError, ValueError):
#             raise ValueError(f"Field '{key}' must be a number")

#     return cleaned


# def build_model_input(cleaned_data):
#     """Convert request values to model input format."""
#     model_input = {
#         "Temperature_C": cleaned_data["temperature"],
#         "Power_On_Hours": cleaned_data["power_on_hours"],
#         "Percent_Life_Used": cleaned_data["life_used"],
#         "Unsafe_Shutdowns": cleaned_data["unsafe_shutdowns"],
#         "Media_Errors": cleaned_data["media_errors"],
#     }
#     return pd.DataFrame([model_input], columns=MODEL_FEATURES)


# def infer_failure_mode(cleaned_data):
#     """Infer failure mode from SMART metrics."""
#     temperature = cleaned_data["temperature"]
#     power_on_hours = cleaned_data["power_on_hours"]
#     life_used = cleaned_data["life_used"]
#     unsafe_shutdowns = cleaned_data["unsafe_shutdowns"]
#     media_errors = cleaned_data["media_errors"]

#     if media_errors >= 10 and power_on_hours < 3000:
#         return FAILURE_MODE_LABELS["early_life"]
#     if temperature >= 70:
#         return FAILURE_MODE_LABELS["thermal"]
#     if unsafe_shutdowns >= 5:
#         return FAILURE_MODE_LABELS["power"]
#     if life_used >= 80:
#         return FAILURE_MODE_LABELS["wear_out"]
#     if media_errors >= 5 or temperature >= 60:
#         return FAILURE_MODE_LABELS["firmware"]
#     return FAILURE_MODE_LABELS["healthy"]


# FAILURE_MODE_DETAILS = {
#     "Healthy": {
#         "label": "Healthy",
#         "description": "Drive appears healthy based on current SMART telemetry."
#     },
#     "Wear-Out Failure": {
#         "label": "Wear-Out Failure",
#         "description": "High drive usage and wear indicate likely end-of-life failure."
#     },
#     "Thermal Failure": {
#         "label": "Thermal Failure",
#         "description": "Temperature is consistently high, which can cause drive degradation."
#     },
#     "Power-Related Failure": {
#         "label": "Power-Related Failure",
#         "description": "Unsafe shutdowns and power instability may damage the drive."
#     },
#     "Firmware/Controller Failure": {
#         "label": "Firmware/Controller Failure",
#         "description": "Errors suggest a firmware or controller-related issue."
#     },
#     "Early-Life Failure": {
#         "label": "Early-Life Failure",
#         "description": "The drive is failing early, likely due to manufacturing or premature stress."
#     },
#     "General Failure": {
#         "label": "General Failure",
#         "description": "Drive metrics indicate a failure risk, but the exact mode is uncertain."
#     },
# }


# def compute_risk_level(probability):
#     if probability >= 0.7:
#         return "HIGH"
#     if probability >= 0.4:
#         return "MEDIUM"
#     return "LOW"


# def build_predict_response(cleaned_data, prediction, probability):
#     failure_mode = "Healthy" if int(prediction) == 0 else classify_failure(
#         cleaned_data["temperature"],
#         cleaned_data["power_on_hours"],
#         cleaned_data["life_used"],
#         cleaned_data["media_errors"],
#         cleaned_data["unsafe_shutdowns"],
#     )
#     details = FAILURE_MODE_DETAILS.get(
#         failure_mode,
#         {
#             "label": failure_mode,
#             "description": "Predicted failure mode based on drive telemetry."
#         }
#     )
#     risk_level = compute_risk_level(probability)

#     return {
#         "success": True,
#         "prediction": failure_mode,
#         "label": "SAFE" if int(prediction) == 0 else "FAIL",
#         "risk_level": risk_level,
#         "failure_mode_label": details["label"],
#         "failure_mode_description": details["description"],
#         "confidence_percent": round(probability * 100, 1),
#         "failure_mode": details["label"],
#         "mode_probabilities": [
#             {"mode": "SAFE", "label": "Safe", "percentage": round((1 - probability) * 100, 1)},
#             {"mode": "FAIL", "label": "Fail", "percentage": round(probability * 100, 1)},
#         ],
#         "warnings": [
#             *(["High temperature is a strong signal for thermal failure."] if cleaned_data["temperature"] >= 70 else []),
#             *(["Many unsafe shutdowns can lead to power-related drive issues."] if cleaned_data["unsafe_shutdowns"] >= 10 else []),
#             *(["Elevated media errors suggest a drive may already be degrading."] if cleaned_data["media_errors"] >= 5 else []),
#             *(["Drive has high life usage and may be near end-of-life."] if cleaned_data["life_used"] >= 80 else []),
#         ],
#         "metrics": {
#             "temperature_c": cleaned_data["temperature"],
#             "power_on_hours": cleaned_data["power_on_hours"],
#             "life_used_percent": cleaned_data["life_used"],
#             "unsafe_shutdowns": int(cleaned_data["unsafe_shutdowns"]),
#             "media_errors": int(cleaned_data["media_errors"]),
#         },
#     }


# # Routes

# @app.route("/", methods=["GET"])
# def home():
#     """Serve index.html for main page."""
#     return render_template("index.html")


# @app.route("/api/health", methods=["GET"])
# @app.route("/health", methods=["GET"])
# def health():
#     """Health check endpoint."""
#     return jsonify({"status": "healthy", "message": "API is running"}), 200


# @app.route("/api/predict", methods=["POST", "OPTIONS"])
# @app.route("/predict", methods=["POST", "OPTIONS"])
# def predict():
#     """
#     Predict drive failure from SMART metrics.
    
#     Expected JSON body:
#     {
#         "temperature": 40,
#         "power_on_hours": 5000,
#         "life_used": 20,
#         "unsafe_shutdowns": 1,
#         "media_errors": 0
#     }
#     """
#     # Handle OPTIONS preflight
#     if request.method == "OPTIONS":
#         return "", 200
    
#     request_data = request.get_json(silent=True)
    
#     try:
#         # Validate input
#         cleaned_data = validate_request_data(request_data)
        
#         # Build model input
#         model_input = build_model_input(cleaned_data)
        
#         # Make prediction
#         prediction = model.predict(model_input)[0]
        
#         # Get probability if available
#         try:
#             probability = float(model.predict_proba(model_input)[0][1])
#         except:
#             probability = 0.0
        
#         # Determine result
#         is_failing = int(prediction) == 1
        
#         response = {
#             "success": True,
#             "prediction": "Failing ⚠️" if is_failing else "Healthy ✓",
#             "failure_risk": f"{probability * 100:.1f}%",
#             "possible_failure_mode": infer_failure_mode(cleaned_data),
#             "metrics": {
#                 "temperature_c": cleaned_data["temperature"],
#                 "power_on_hours": cleaned_data["power_on_hours"],
#                 "life_used_percent": cleaned_data["life_used"],
#                 "unsafe_shutdowns": int(cleaned_data["unsafe_shutdowns"]),
#                 "media_errors": int(cleaned_data["media_errors"]),
#             }
#         }
#         return jsonify(response), 200

#     except ValueError as err:
#         return jsonify({"success": False, "error": str(err)}), 400
#     except Exception as err:
#         print(f"Prediction error: {err}")
#         return jsonify({"success": False, "error": "Prediction failed. Check server logs."}), 500


# if __name__ == "__main__":
#     print("\n" + "="*60)
#     print("🚀 NVMe Drive Failure Predictor API")
#     print("="*60)
#     print(f"📍 Starting on http://0.0.0.0:5000")
#     print(f"🔗 Frontend will connect to http://localhost:5000")
#     print("\nAPI Endpoints:")
#     print("  GET  /api/health       - Check if API is running")
#     print("  POST /api/predict      - Predict drive failure")
#     print("="*60 + "\n")
    
#     app.run(host="0.0.0.0", port=5000, debug=False)

import os
import joblib
import pandas as pd
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

# ==============================
# App Setup
# ==============================
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# ==============================
# Load Model
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "ml-model", "nvme_failure_mode_model.pkl")
COLUMNS_PATH = os.path.join(BASE_DIR, "ml-model", "feature_columns.pkl")

model = joblib.load(MODEL_PATH)
feature_columns = joblib.load(COLUMNS_PATH)

# ==============================
# Failure Mode Definitions
# ==============================
FAILURE_MODES = {
    0: "Healthy",
    1: "Wear-Out Failure",
    2: "Thermal Failure",
    3: "Power-Related Failure",
    4: "Controller/Firmware Failure",
    5: "Early-Life Failure",
}

# ==============================
# Input Validation
# ==============================
def validate_input(data):
    if not isinstance(data, dict):
        raise ValueError("Invalid JSON input")

    required = ["temperature", "power_on_hours", "life_used"]

    validated = {}
    for field in required:
        if field not in data:
            raise ValueError(f"Missing field: {field}")
        validated[field] = float(data[field])

    # Optional fields
    validated["unsafe_shutdowns"] = float(data.get("unsafe_shutdowns", 0))
    validated["media_errors"] = float(data.get("media_errors", 0))

    return validated

# ==============================
# Build Model Input
# ==============================
def build_model_input(data):
    df = pd.DataFrame([{
        "Temperature_C": data["temperature"],
        "Power_On_Hours": data["power_on_hours"],
        "Percent_Life_Used": data["life_used"],
        "Unsafe_Shutdowns": data["unsafe_shutdowns"],
        "Media_Errors": data["media_errors"],
    }])

    # Align columns with training
    df = df.reindex(columns=feature_columns, fill_value=0)

    return df

# ==============================
# Optional Explainability (Rules)
# ==============================
def explain_failure(data):
    if data["media_errors"] >= 10 and data["power_on_hours"] < 3000:
        return "Early-Life Failure"
    if data["temperature"] >= 70:
        return "Thermal Failure"
    if data["unsafe_shutdowns"] >= 5:
        return "Power-Related Failure"
    if data["life_used"] >= 80:
        return "Wear-Out Failure"
    if data["media_errors"] >= 5:
        return "Controller/Firmware Failure"
    return "Healthy"

# ==============================
# Routes
# ==============================

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "model_loaded": True})

@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(silent=True)
        validated = validate_input(data)

        # Build input
        df = build_model_input(validated)

        # ML Prediction
        pred_class = int(model.predict(df)[0])
        pred_proba = model.predict_proba(df)[0]

        # Determine health
        is_failing = pred_class != 0

        # Confidence
        confidence = float(pred_proba[pred_class])

        # Optional explainability
        rule_based_mode = explain_failure(validated)

        # Build response
        response = {
            "success": True,
            "health": "Failing" if is_failing else "Healthy",
            "predicted_mode": pred_class,
            "mode_name": FAILURE_MODES[pred_class],
            "confidence": round(confidence, 4),

            # All probabilities
            "all_modes": [
                {
                    "mode": i,
                    "name": FAILURE_MODES.get(i, "Unknown"),
                    "probability": round(float(pred_proba[i]), 4),
                    "percentage": round(float(pred_proba[i]) * 100, 1),
                }
                for i in range(len(pred_proba))
            ],

            # Explainability
            "rule_based_explanation": rule_based_mode,

            "input_summary": validated
        }

        return jsonify(response), 200

    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400

    except Exception as e:
        return jsonify({"success": False, "error": f"Prediction failed: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
