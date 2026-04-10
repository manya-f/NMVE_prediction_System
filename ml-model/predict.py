# =============================================================================
# predict.py  —  NVMe Drive Failure Prediction  (Inference)
# =============================================================================
# Loads the RandomForestClassifier saved by train.py and predicts whether a
# single NVMe drive is SAFE or likely to FAIL, together with a probability.
#
# ── Preprocessing mirrors train.py exactly ────────────────────────────────────
#   1. Drop leakage / identifier columns
#      (Drive_ID, Failure_Mode, Failure_Flag, SMART_Warning_Flag)
#   2. One-hot encode categorical columns with pd.get_dummies
#   3. Align resulting columns to the training schema:
#        – missing dummy columns  → filled with 0
#        – extra / unseen columns → dropped
#
# ── Usage ─────────────────────────────────────────────────────────────────────
#   • Edit the sample_* dicts below and run:  python predict.py
#   • Or import predict_drive(sample: dict) into your own pipeline.
#
# Dependencies: pandas, numpy, scikit-learn, joblib  (standard ML stack)
# =============================================================================

import os
import warnings
warnings.filterwarnings("ignore")

import numpy  as np
import pandas as pd
import joblib

# ── Configuration ─────────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH   = os.path.join(BASE_DIR, "nvme_rf_model.pkl")
COLUMNS_PATH = os.path.join(BASE_DIR, "feature_columns.pkl")

# Same set as in train.py — silently ignored if absent from the input dict
LEAKAGE_COLS = [
    "Drive_ID",
    "Failure_Mode",
    "Failure_Flag",
    "SMART_Warning_Flag",
]


# ==============================================================================
# Utility
# ==============================================================================
def banner(title=""):
    width = 60
    if title:
        pad  = (width - len(title) - 2) // 2
        line = "─" * pad + f" {title} " + "─" * pad
        line = line[:width].ljust(width, "─")
    else:
        line = "─" * width
    print(line)


# ==============================================================================
# Core inference function
# ==============================================================================
def predict_drive(sample: dict) -> dict:
    """
    Predict whether an NVMe drive is SAFE or FAIL.

    Parameters
    ----------
    sample : dict
        Raw drive attributes using the original CSV column names.
        Leakage keys (Drive_ID, Failure_Mode, Failure_Flag,
        SMART_Warning_Flag) are silently dropped if present.

    Returns
    -------
    dict
        predicted_class : int    (0 = SAFE, 1 = FAIL)
        label           : str    ('SAFE' or 'FAIL')
        prob_safe       : float  probability of being SAFE
        prob_fail       : float  probability of being FAIL
        feature_vector  : pd.DataFrame  (1 row, aligned to training schema)
    """
    # ── Load saved artifacts ──────────────────────────────────────────────────
    for path in (MODEL_PATH, COLUMNS_PATH):
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"'{path}' not found. Run train.py first to generate it."
            )

    clf             = joblib.load(MODEL_PATH)
    feature_columns = joblib.load(COLUMNS_PATH)

    # ── Convert to single-row DataFrame ──────────────────────────────────────
    df = pd.DataFrame([sample])

    # ── Drop leakage / identifier columns (ignore absent ones) ───────────────
    cols_to_drop = [c for c in LEAKAGE_COLS if c in df.columns]
    if cols_to_drop:
        df.drop(columns=cols_to_drop, inplace=True)

    # ── One-hot encode categorical columns ────────────────────────────────────
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    if cat_cols:
        df = pd.get_dummies(df, columns=cat_cols, drop_first=False)

    # ── Align to training schema ──────────────────────────────────────────────
    # reindex:  adds any missing dummy columns (→ 0), drops unseen columns
    df = df.reindex(columns=feature_columns, fill_value=0)

    # ── Predict ───────────────────────────────────────────────────────────────
    pred_class = int(clf.predict(df)[0])
    pred_proba = clf.predict_proba(df)[0]   # [P(SAFE), P(FAIL)]
    prob_safe  = float(pred_proba[0])
    prob_fail  = float(pred_proba[1])

    return {
        "predicted_class" : pred_class,
        "label"           : "SAFE" if pred_class == 0 else "FAIL",
        "prob_safe"       : prob_safe,
        "prob_fail"       : prob_fail,
        "feature_vector"  : df,
    }


# ==============================================================================
# Sample inputs
# ==============================================================================

# ── Sample A : Healthy drive (expected → SAFE) ────────────────────────────────
sample_healthy = {
    # Identifier — will be silently dropped
    "Drive_ID"          : "NVME-TEST-HEALTHY",

    # Categorical features
    "Vendor"            : "VendorA",
    "Model"             : "Model-PRO",
    "Firmware_Version"  : "FW2.1",

    # SMART / usage metrics
    "Power_On_Hours"    : 8_500,    # moderate hours on
    "Total_TBW_TB"      : 45.0,     # low write wear
    "Total_TBR_TB"      : 40.0,
    "Temperature_C"     : 35.0,     # comfortably cool
    "Percent_Life_Used" : 12.0,     # drive is mostly new
    "Media_Errors"      : 0,
    "Unsafe_Shutdowns"  : 1,
    "CRC_Errors"        : 0,
    "Read_Error_Rate"   : 1.5,
    "Write_Error_Rate"  : 0.8,
    # SMART_Warning_Flag intentionally omitted — it's a leakage column.
    # If it appears in real data it is automatically dropped.
}

# ── Sample B : Stressed drive (expected → FAIL or high risk) ─────────────────
sample_stressed = {
    "Drive_ID"          : "NVME-TEST-STRESSED",

    "Vendor"            : "VendorB",
    "Model"             : "Model-ULTRA",
    "Firmware_Version"  : "FW1.0",

    "Power_On_Hours"    : 52_000,   # very high hours
    "Total_TBW_TB"      : 420.0,    # heavy write wear
    "Total_TBR_TB"      : 380.0,
    "Temperature_C"     : 63.0,     # running hot
    "Percent_Life_Used" : 95.0,     # near end-of-life
    "Media_Errors"      : 6,        # multiple media errors
    "Unsafe_Shutdowns"  : 9,
    "CRC_Errors"        : 5,
    "Read_Error_Rate"   : 28.0,     # very high error rate
    "Write_Error_Rate"  : 22.0,
}


# ==============================================================================
# Display helper
# ==============================================================================
def display_result(section_label: str, sample: dict, result: dict) -> None:
    banner(section_label)

    # Print input (skip leakage keys for clarity)
    print("Drive attributes (input):")
    for k, v in sample.items():
        if k not in LEAKAGE_COLS:
            print(f"  {k:<25s}: {v}")

    # Prediction
    print()
    icon = "✅" if result["predicted_class"] == 0 else "⚠️ "
    print(f"  Prediction  : {icon}  {result['label']}")
    print(f"  P(SAFE)     : {result['prob_safe']:.4f}  "
          f"({result['prob_safe'] * 100:.1f} %)")
    print(f"  P(FAIL)     : {result['prob_fail']:.4f}  "
          f"({result['prob_fail'] * 100:.1f} %)")

    # Risk-tier recommendation
    p_fail = result["prob_fail"]
    print()
    if p_fail >= 0.70:
        print("  🔴 HIGH RISK   — Back up data immediately; replace drive.")
    elif p_fail >= 0.40:
        print("  🟠 MEDIUM RISK — Monitor closely; schedule proactive replacement.")
    elif p_fail >= 0.15:
        print("  🟡 LOW RISK    — Watch SMART stats at next maintenance window.")
    else:
        print("  🟢 HEALTHY     — No immediate action required.")


# ==============================================================================
# Main
# ==============================================================================
if __name__ == "__main__":
    banner("NVMe Drive Failure — Inference Script")

    # Confirm artifacts exist and print basic info
    for path in (MODEL_PATH, COLUMNS_PATH):
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"'{path}' not found. Run train.py first."
            )
    feature_columns = joblib.load(COLUMNS_PATH)
    print(f"Model file     : {MODEL_PATH}")
    print(f"Columns file   : {COLUMNS_PATH}")
    print(f"Features used  : {len(feature_columns)}")

    # Run both predictions
    result_healthy  = predict_drive(sample_healthy)
    result_stressed = predict_drive(sample_stressed)

    # Display results
    display_result("Sample A — Healthy Drive",  sample_healthy,  result_healthy)
    display_result("Sample B — Stressed Drive", sample_stressed, result_stressed)

    banner()
    print("✅  Inference complete.")
    banner()
