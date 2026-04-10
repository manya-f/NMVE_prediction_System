# """
# NVMe Drive Failure Prediction Flask API
# Serves single-drive predictions with all 6 failure mode probabilities
# """

# import os
# import sys
# import joblib
# import pandas as pd
# from flask import Flask, jsonify, request, render_template
# from flask_cors import CORS

# # Add ml-model to path for imports
# ML_MODEL_DIR = os.path.join(os.path.dirname(__file__), "ml-model")
# if ML_MODEL_DIR not in sys.path:
#     sys.path.insert(0, ML_MODEL_DIR)

# app = Flask(__name__, template_folder="templates", static_folder="static")
# CORS(app)

# # ============================================================================
# # Model Configuration
# # ============================================================================
# MODEL_PATH = os.path.join(ML_MODEL_DIR, "nvme_failure_mode_model.pkl")
# COLUMNS_PATH = os.path.join(ML_MODEL_DIR, "feature_columns.pkl")

# FAILURE_MODES = {
#     0: {"name": "Healthy", "description": "No abnormal metrics"},
#     1: {"name": "Wear-Out Failure", "description": "High TBW, nearing end-of-life"},
#     2: {"name": "Thermal Failure", "description": "High temperature stress"},
#     3: {"name": "Power-Related Failure", "description": "Power stability issues"},
#     4: {"name": "Controller/Firmware Failure", "description": "Firmware/controller instability"},
#     5: {"name": "Rapid Error Accumulation", "description": "Manufacturing defect"},
# }

# # Validate model files exist
# if not os.path.exists(MODEL_PATH):
#     raise FileNotFoundError(
#         f"Model not found at {MODEL_PATH}. Run ml-model/train_failure_modes.py first."
#     )

# if not os.path.exists(COLUMNS_PATH):
#     raise FileNotFoundError(
#         f"Feature columns not found at {COLUMNS_PATH}. Run ml-model/train_failure_modes.py first."
#     )

# # Load model and feature schema
# try:
#     model = joblib.load(MODEL_PATH)
#     feature_columns = joblib.load(COLUMNS_PATH)
# except Exception as e:
#     raise Exception(f"Failed to load model: {str(e)}")

# # ============================================================================
# # Input Validation
# # ============================================================================
# REQUIRED_FIELDS = ["temperature", "power_on_hours", "life_used"]
# OPTIONAL_FIELDS = ["unsafe_shutdowns", "media_errors"]
# MODEL_FEATURES = [
#     "Temperature_C",
#     "Power_On_Hours",
#     "Percent_Life_Used",
#     "Unsafe_Shutdowns",
#     "Media_Errors",
# ]

# LEAKAGE_COLS = ["Drive_ID", "Failure_Mode", "Failure_Flag", "SMART_Warning_Flag"]


# def validate_input(data):
#     """Validate and clean user input."""
#     if not isinstance(data, dict):
#         raise ValueError("Invalid JSON payload")

#     validated = {}

#     # Check required fields
#     for field in REQUIRED_FIELDS:
#         if field not in data:
#             raise ValueError(f"Missing required field: {field}")
#         try:
#             validated[field] = float(data[field])
#         except (TypeError, ValueError):
#             raise ValueError(f"Field '{field}' must be a number")

#     # Optional fields default to 0
#     for field in OPTIONAL_FIELDS:
#         try:
#             validated[field] = float(data.get(field, 0))
#         except (TypeError, ValueError):
#             validated[field] = 0

#     return validated


# def build_model_input(validated_data):
#     """Convert validated input to model input format."""
#     return {
#         "Temperature_C": validated_data["temperature"],
#         "Power_On_Hours": validated_data["power_on_hours"],
#         "Percent_Life_Used": validated_data["life_used"],
#         "Unsafe_Shutdowns": validated_data["unsafe_shutdowns"],
#         "Media_Errors": validated_data["media_errors"],
#     }


# def predict_failure_modes(model_input):
#     """Use ML model to predict all 6 failure modes."""
#     # Convert to DataFrame
#     df = pd.DataFrame([model_input])

#     # Drop leakage columns if present
#     cols_to_drop = [c for c in LEAKAGE_COLS if c in df.columns]
#     if cols_to_drop:
#         df.drop(columns=cols_to_drop, inplace=True)

#     # One-hot encode categorical columns (if any)
#     cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
#     if cat_cols:
#         df = pd.get_dummies(df, columns=cat_cols, drop_first=False)

#     # Align to training schema
#     df = df.reindex(columns=feature_columns, fill_value=0)

#     # Predict
#     pred_class = int(model.predict(df)[0])
#     pred_proba = model.predict_proba(df)[0]

#     return pred_class, pred_proba


# def infer_failure_mode_heuristics(validated_data):
#     """Heuristic-based failure mode detection for explainability."""
#     temp = validated_data["temperature"]
#     power_hours = validated_data["power_on_hours"]
#     life_used = validated_data["life_used"]
#     unsafe_shutdowns = validated_data["unsafe_shutdowns"]
#     media_errors = validated_data["media_errors"]

#     if media_errors >= 10 and power_hours < 3000:
#         return 5  # Rapid Error Accumulation
#     if temp >= 70:
#         return 2  # Thermal Failure
#     if unsafe_shutdowns >= 5:
#         return 3  # Power-Related
#     if life_used >= 80:
#         return 1  # Wear-Out
#     if media_errors >= 5:
#         return 4  # Firmware
#     return 0  # Healthy


# # ============================================================================
# # Routes
# # ============================================================================

# @app.route("/", methods=["GET"])
# def home():
#     """Serve the main UI."""
#     return render_template("index.html")


# @app.route("/api/predict", methods=["POST"])
# def predict():
#     """
#     Predict failure mode for a single NVMe drive.

#     Request JSON:
#     {
#         "temperature": 45.5,
#         "power_on_hours": 15000,
#         "life_used": 62,
#         "unsafe_shutdowns": 2,      (optional, default 0)
#         "media_errors": 1           (optional, default 0)
#     }

#     Response JSON:
#     {
#         "success": true,
#         "health": "Healthy",
#         "predicted_mode": 0,
#         "mode_name": "Healthy",
#         "mode_description": "No abnormal metrics",
#         "failure_modes": [
#             {"mode": 0, "name": "Healthy", "probability": 0.89},
#             {"mode": 1, "name": "Wear-Out Failure", "probability": 0.06},
#             ...
#         ],
#         "top_risk_mode": {"mode": 1, "name": "Wear-Out Failure"},
#         "confidence": 0.89
#     }
#     """
#     try:
#         # Validate input
#         data = request.get_json(silent=True)
#         if data is None:
#             return jsonify({"success": False, "error": "Empty request body"}), 400

#         validated_data = validate_input(data)

#         # Build model input and predict
#         model_input = build_model_input(validated_data)
#         pred_class, pred_proba = predict_failure_modes(model_input)

#         # Determine overall health
#         is_failing = pred_class == 1
#         health = "Failing" if is_failing else "Healthy"

#         # Get top failure mode from heuristics
#         top_mode = infer_failure_mode_heuristics(validated_data)

#         # Build failure modes array with probabilities
#         failure_modes = []
#         for i in range(6):
#             mode_info = FAILURE_MODES.get(i, {})
#             failure_modes.append({
#                 "mode": i,
#                 "name": mode_info.get("name", "Unknown"),
#                 "description": mode_info.get("description", ""),
#                 "probability": round(float(pred_proba[i] if i < len(pred_proba) else 0), 4),
#                 "percentage": round(float(pred_proba[i] if i < len(pred_proba) else 0) * 100, 1),
#             })

#         # Sort by probability (descending)
#         failure_modes_sorted = sorted(failure_modes, key=lambda x: x["probability"], reverse=True)

#         response = {
#             "success": True,
#             "health": health,
#             "predicted_mode": top_mode,
#             "mode_name": FAILURE_MODES[top_mode]["name"],
#             "mode_description": FAILURE_MODES[top_mode]["description"],
#             "failure_modes": failure_modes_sorted,
#             "top_risk_mode": {
#                 "mode": failure_modes_sorted[1]["mode"] if failure_modes_sorted[1]["mode"] != top_mode else failure_modes_sorted[2]["mode"],
#                 "name": failure_modes_sorted[1]["name"] if failure_modes_sorted[1]["mode"] != top_mode else failure_modes_sorted[2]["name"],
#             },
#             "confidence": round(float(max(pred_proba)), 4),
#         }

#         return jsonify(response), 200

#     except ValueError as e:
#         return jsonify({"success": False, "error": str(e)}), 400
#     except Exception as e:
#         return jsonify({"success": False, "error": f"Prediction failed: {str(e)}"}), 500


# @app.route("/api/health", methods=["GET"])
# def health_check():
#     """Health check endpoint."""
#     return jsonify({"status": "ok", "model_loaded": model is not None}), 200


# # ============================================================================
# # Error Handlers
# # ============================================================================

# @app.errorhandler(404)
# def not_found(error):
#     return jsonify({"error": "Endpoint not found"}), 404


# @app.errorhandler(500)
# def internal_error(error):
#     return jsonify({"error": "Internal server error"}), 500


# # ============================================================================
# # Main
# # ============================================================================

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)

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