from flask import Flask, jsonify, request
from flask_cors import CORS
import joblib
import os
import pandas as pd

app = Flask(__name__)
CORS(app)

MODE_MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "ml-model", "nvme_failure_mode_model.pkl"
)
MODE_COLUMNS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "ml-model", "feature_columns.pkl"
)

mode_model = joblib.load(MODE_MODEL_PATH)
mode_feature_columns = joblib.load(MODE_COLUMNS_PATH)

REQUIRED_FIELDS = {
    "Vendor": str,
    "Model": str,
    "Firmware_Version": str,
    "Temperature_C": float,
    "Total_TBW_TB": float,
    "Total_TBR_TB": float,
    "Power_On_Hours": float,
    "Unsafe_Shutdowns": float,
    "Media_Errors": float,
    "Percent_Life_Used": float,
    "Available_Spare": float,
    "SMART_Warning_Flag": float,
}

FIELD_ALIASES = {
    "Vendor": ["Vendor"],
    "Model": ["Model"],
    "Firmware_Version": ["Firmware_Version"],
    "Temperature_C": ["Temperature_C", "temperature"],
    "Total_TBW_TB": ["Total_TBW_TB"],
    "Total_TBR_TB": ["Total_TBR_TB"],
    "Power_On_Hours": ["Power_On_Hours", "power_on_hours"],
    "Unsafe_Shutdowns": ["Unsafe_Shutdowns", "unsafe_shutdowns"],
    "Media_Errors": ["Media_Errors", "media_errors", "error_count"],
    "Percent_Life_Used": ["Percent_Life_Used", "life_used"],
    "Available_Spare": ["Available_Spare"],
    "SMART_Warning_Flag": ["SMART_Warning_Flag"],
}

FAILURE_MODE_DETAILS = {
    0: {
        "label": "Healthy",
        "description": "No abnormal metrics, no error patterns detected.",
        "risk_level": "LOW",
        "recommendation": "Drive is healthy. Continue regular SMART monitoring.",
        "recommendation_points": [
            "Continue periodic SMART health checks and review the trend over time.",
            "Keep firmware on the latest vendor-approved version.",
            "Maintain good airflow and stable operating temperatures.",
            "Verify backup and restore routines even for healthy drives.",
            "Review endurance usage monthly to catch wear progression early.",
        ],
    },
    1: {
        "label": "Wear-Out Failure",
        "description": "High TBW or percent life used; flash nearing end-of-life.",
        "risk_level": "MEDIUM",
        "recommendation": "Drive wear is elevated. Plan replacement and monitor endurance closely.",
        "recommendation_points": [
            "Plan a replacement before endurance reaches a critical limit.",
            "Reduce write-heavy workloads where possible.",
            "Increase monitoring frequency for TBW and life-used metrics.",
            "Verify backups and test recovery before migration.",
            "Schedule a maintenance window to retire the drive cleanly.",
        ],
    },
    2: {
        "label": "Thermal Failure",
        "description": "Consistently high temperature (typically >70°C) causing error spikes.",
        "risk_level": "HIGH",
        "recommendation": "Thermal risk is high. Improve cooling and reduce sustained thermal stress.",
        "recommendation_points": [
            "Improve chassis airflow or add targeted NVMe cooling.",
            "Inspect heatsink contact and thermal pad placement.",
            "Reduce sustained I/O bursts until temperatures stabilize.",
            "Review ambient temperature and fan profile behavior.",
            "Re-run diagnostics after cooling changes to confirm improvement.",
        ],
    },
    3: {
        "label": "Power-Related Failure",
        "description": "Multiple unsafe shutdowns leading to corruption or CRC errors.",
        "risk_level": "HIGH",
        "recommendation": "Investigate power stability, unsafe shutdowns, and storage cabling immediately.",
        "recommendation_points": [
            "Inspect PSU stability and recent abrupt shutdown events.",
            "Review OS logs for improper shutdown or reset patterns.",
            "Check motherboard slot condition and reseat the drive if needed.",
            "Use UPS or protected power if supply quality is unstable.",
            "Back up critical data immediately before further troubleshooting.",
        ],
    },
    4: {
        "label": "Controller/Firmware Failure",
        "description": "Issues tied to specific firmware versions or controller instability.",
        "risk_level": "MEDIUM",
        "recommendation": "Review firmware and controller health. Consider diagnostics, firmware update, or replacement.",
        "recommendation_points": [
            "Compare the firmware version against the latest vendor release.",
            "Run vendor diagnostics for controller and media integrity.",
            "Review recurring resets or I/O errors in system logs.",
            "Avoid firmware changes without a verified backup and rollback plan.",
            "Replace the drive if instability persists after diagnostics.",
        ],
    },
    5: {
        "label": "Rapid Error Accumulation (Early-Life Failure)",
        "description": "High error rate in early usage (<3000 hours), likely manufacturing defect.",
        "risk_level": "HIGH",
        "recommendation": "Failure pattern suggests early defect behavior. Back up data and consider warranty replacement.",
        "recommendation_points": [
            "Back up all important data immediately.",
            "Remove the drive from critical production workloads.",
            "Run a full vendor diagnostic and save the report.",
            "Check warranty status and prepare an RMA if applicable.",
            "Compare the issue with other drives from the same batch or firmware family.",
        ],
    },
}


def compute_binary_risk(probabilities):
    healthy_probability = probabilities[0] if len(probabilities) > 0 else 0.0
    return float(1.0 - healthy_probability)


def validate_input(data):
    if not isinstance(data, dict):
        return False, "Input must be a JSON object", None

    validated = {}
    for field, caster in REQUIRED_FIELDS.items():
        raw_value = None
        for alias in FIELD_ALIASES[field]:
            if alias in data:
                raw_value = data[alias]
                break

        if raw_value is None or raw_value == "":
            return False, f"Missing required field: {' or '.join(FIELD_ALIASES[field])}", None

        try:
            if caster is str:
                validated[field] = str(raw_value)
            else:
                validated[field] = float(raw_value)
        except (TypeError, ValueError):
            return False, f"Field '{field}' must be a valid {caster.__name__}", None

    if not (0 <= validated["Percent_Life_Used"] <= 100):
        return False, "Field 'Percent_Life_Used' must be between 0 and 100", None

    if not (0 <= validated["Available_Spare"] <= 100):
        return False, "Field 'Available_Spare' must be between 0 and 100", None

    if validated["SMART_Warning_Flag"] not in (0.0, 1.0):
        return False, "Field 'SMART_Warning_Flag' must be 0 or 1", None

    return True, None, validated


def build_mode_model_input(cleaned_data):
    row = {
        "Vendor": cleaned_data["Vendor"],
        "Model": cleaned_data["Model"],
        "Firmware_Version": cleaned_data["Firmware_Version"],
        "Temperature_C": cleaned_data["Temperature_C"],
        "Total_TBW_TB": cleaned_data["Total_TBW_TB"],
        "Total_TBR_TB": cleaned_data["Total_TBR_TB"],
        "Power_On_Hours": cleaned_data["Power_On_Hours"],
        "Unsafe_Shutdowns": cleaned_data["Unsafe_Shutdowns"],
        "Media_Errors": cleaned_data["Media_Errors"],
        "Percent_Life_Used": cleaned_data["Percent_Life_Used"],
        "Available_Spare": cleaned_data["Available_Spare"],
        "SMART_Warning_Flag": cleaned_data["SMART_Warning_Flag"],
    }

    df = pd.DataFrame([row])
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    if cat_cols:
        df = pd.get_dummies(df, columns=cat_cols, drop_first=False)

    return df.reindex(columns=mode_feature_columns, fill_value=0)


def predict_failure_mode(cleaned_data):
    df = build_mode_model_input(cleaned_data)
    predicted_mode = int(mode_model.predict(df)[0])
    predicted_probabilities = mode_model.predict_proba(df)[0]

    mode_probabilities = []
    for mode in range(6):
        probability = float(predicted_probabilities[mode]) if mode < len(predicted_probabilities) else 0.0
        details = FAILURE_MODE_DETAILS[mode]
        mode_probabilities.append({
            "mode": mode,
            "label": details["label"],
            "probability": round(probability, 4),
            "percentage": round(probability * 100, 1),
        })

    return predicted_mode, predicted_probabilities, mode_probabilities


def build_predict_response(cleaned_data, predicted_mode, predicted_probabilities, mode_probabilities):
    details = FAILURE_MODE_DETAILS[predicted_mode]
    confidence_percent = next(
        item["percentage"] for item in mode_probabilities if item["mode"] == predicted_mode
    )
    fail_probability = compute_binary_risk(predicted_probabilities)

    return {
        "success": True,
        "prediction": details["label"],
        "label": "SAFE" if predicted_mode == 0 else "FAIL",
        "health": "Healthy" if predicted_mode == 0 else "Failing",
        "predicted_mode": predicted_mode,
        "failure_mode": details["label"],
        "failure_mode_label": details["label"],
        "failure_mode_description": details["description"],
        "confidence_percent": confidence_percent,
        "risk_level": details["risk_level"],
        "recommendation": details["recommendation"],
        "recommendation_points": details["recommendation_points"],
        "mode_probabilities": mode_probabilities,
        "binary_probabilities": [
            {"mode": "SAFE", "label": "Safe", "percentage": round((1 - fail_probability) * 100, 1)},
            {"mode": "FAIL", "label": "Fail", "percentage": round(fail_probability * 100, 1)},
        ],
        "warnings": [],
        "submitted_inputs": cleaned_data,
    }


@app.route('/api/predict', methods=['POST', 'OPTIONS'])
@app.route('/predict', methods=['POST', 'OPTIONS'])
@app.route('/api/predict/single', methods=['POST', 'OPTIONS'])
@app.route('/predict/single', methods=['POST', 'OPTIONS'])
def predict():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200

    try:
        data = request.get_json(silent=True)
        is_valid, error_msg, validated_data = validate_input(data)
        if not is_valid:
            return jsonify({"error": error_msg}), 400

        predicted_mode, predicted_probabilities, mode_probabilities = predict_failure_mode(validated_data)
        response = build_predict_response(
            validated_data,
            predicted_mode,
            predicted_probabilities,
            mode_probabilities,
        )
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500


@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
