# =============================================================================
# train.py  —  NVMe Drive Failure Prediction
# =============================================================================
# Dataset : NVMe_Drive_Failure_Dataset.csv  (10 000 rows × 17 columns)
#
# Target  : Binary label derived from Failure_Mode
#             Failure_Mode == 0  →  0  (SAFE)
#             Failure_Mode  > 0  →  1  (FAIL)
#
# ── Columns REMOVED before training (data-leakage / identifiers) ─────────────
#   Drive_ID          – unique identifier, no predictive value
#   Failure_Mode      – direct source of the target label
#   Failure_Flag      – pre-computed binary target (perfectly correlated)
#   SMART_Warning_Flag– perfectly correlated with Failure_Flag
#
# ── Class imbalance (≈ 98 % SAFE / 2 % FAIL) ─────────────────────────────────
#   Handled with TWO complementary strategies (no extra library needed):
#     1. class_weight='balanced'  inside RandomForestClassifier
#     2. Manual minority-class oversampling on the training split
#        (random duplication + tiny Gaussian noise = lightweight SMOTE)
#
# ── Outputs ───────────────────────────────────────────────────────────────────
#   nvme_rf_model.pkl     – trained RandomForestClassifier
#   feature_columns.pkl   – ordered list of feature column names
#
# Dependencies: pandas, numpy, scikit-learn, joblib  (standard ML stack)
# =============================================================================

import os
import warnings
warnings.filterwarnings("ignore")

import numpy  as np
import pandas as pd
import joblib

from sklearn.ensemble        import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics         import (accuracy_score, precision_score,
                                     recall_score,   f1_score,
                                     classification_report, confusion_matrix,
                                     roc_auc_score)

# ── Configuration ─────────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR     = os.path.dirname(BASE_DIR)
DATA_PATH    = os.path.join(ROOT_DIR, "data", "NVMe_Drive_Failure_Dataset.csv")
MODEL_PATH   = os.path.join(BASE_DIR, "nvme_rf_model.pkl")
SIMPLE_MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")  # For simplified API
COLUMNS_PATH = os.path.join(BASE_DIR, "feature_columns.pkl")
RANDOM_STATE = 42
TEST_SIZE    = 0.20

# Removed BEFORE any feature engineering to prevent data leakage
LEAKAGE_COLS = [
    "Drive_ID",            # unique ID — no predictive signal
    "Failure_Mode",        # source of the target → direct leakage
    "Failure_Flag",        # pre-computed binary target → direct leakage
    "SMART_Warning_Flag",  # perfectly correlated with Failure_Flag → leakage
]


# ==============================================================================
# Utility helpers
# ==============================================================================
def banner(title=""):
    """Print a section separator with an optional centred title."""
    width = 65
    if title:
        pad  = (width - len(title) - 2) // 2
        line = "─" * pad + f" {title} " + "─" * pad
        line = line[:width].ljust(width, "─")
    else:
        line = "─" * width
    print(line)


def oversample_minority(X: np.ndarray, y: np.ndarray,
                        rng: np.random.Generator) -> tuple:
    """
    Upsample every minority class to match the majority class size.

    Each synthetic sample is a randomly chosen minority-class row plus
    tiny Gaussian noise (σ = 1 % of each feature's std-dev).  This gives
    the Random Forest genuine variety and avoids the need for the
    imbalanced-learn library.

    Parameters
    ----------
    X   : 2-D numpy array of features  (float-compatible)
    y   : 1-D numpy array of integer labels
    rng : numpy random Generator (for reproducibility)

    Returns
    -------
    X_res, y_res : balanced, shuffled arrays
    """
    classes, counts = np.unique(y, return_counts=True)
    majority_count  = counts.max()
    X_parts, y_parts = [X], [y]

    for cls, cnt in zip(classes, counts):
        if cnt < majority_count:
            idx      = np.where(y == cls)[0]
            needed   = majority_count - cnt
            chosen   = rng.choice(idx, size=needed, replace=True)
            X_chosen = X[chosen].astype(float)

            # Tiny noise so every synthetic row is unique
            noise_scale = X_chosen.std(axis=0) * 0.01
            noise_scale[noise_scale == 0] = 1e-6   # guard flat features
            X_syn = X_chosen + rng.normal(0, noise_scale, X_chosen.shape)

            X_parts.append(X_syn)
            y_parts.append(np.full(needed, cls))

    X_res = np.vstack(X_parts)
    y_res = np.concatenate(y_parts)

    # Shuffle so class blocks are interleaved
    perm = rng.permutation(len(y_res))
    return X_res[perm], y_res[perm]


# ==============================================================================
# 1. Load Data
# ==============================================================================
banner("1 · Load Data")

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(
        f"Dataset not found at '{DATA_PATH}'.\n"
        "Place NVMe_Drive_Failure_Dataset.csv in the same folder as train.py."
    )

df = pd.read_csv(DATA_PATH)
print(f"Loaded : {df.shape[0]:,} rows  ×  {df.shape[1]} columns")
print(f"Columns: {df.columns.tolist()}")

# ==============================================================================
# 2. Build Binary Target  (from Failure_Mode, as specified)
# ==============================================================================
banner("2 · Build Binary Target")

if "Failure_Mode" not in df.columns:
    raise ValueError("'Failure_Mode' column not found. Check the CSV.")

# Failure_Mode == 0  →  0  (SAFE)
# Failure_Mode  > 0  →  1  (FAIL)   [modes 1, 4, 5 seen in this dataset]
df["target"] = (df["Failure_Mode"] != 0).astype(int)

total      = len(df)
safe_count = int((df["target"] == 0).sum())
fail_count = int((df["target"] == 1).sum())

print(f"SAFE (0) : {safe_count:,}  ({safe_count / total * 100:.1f} %)")
print(f"FAIL (1) : {fail_count:,}  ({fail_count / total * 100:.1f} %)")
print(f"Imbalance ratio ≈ {safe_count // fail_count}:1  "
      "→ oversampling + class_weight='balanced' will compensate")

# ==============================================================================
# 3. Drop Leakage / Identifier Columns
# ==============================================================================
banner("3 · Drop Leakage Columns")

cols_to_drop = [c for c in LEAKAGE_COLS if c in df.columns]
df.drop(columns=cols_to_drop, inplace=True)
print(f"Dropped  : {cols_to_drop}")
print(f"Remaining: {df.columns.tolist()}")

# ==============================================================================
# 4. Remove Duplicate Rows
# ==============================================================================
banner("4 · Duplicates")

before = len(df)
df.drop_duplicates(inplace=True)
after  = len(df)
print(f"Removed {before - after} duplicate row(s).  Rows remaining: {after:,}")

# ==============================================================================
# 5. Handle Missing Values
# ==============================================================================
banner("5 · Missing Values")

missing = df.isnull().sum()
missing = missing[missing > 0]

if missing.empty:
    print("No missing values — dataset is complete.")
else:
    print(f"Missing values detected:\n{missing}\n")
    # Numeric columns (excluding the target) → fill with median
    num_cols = df.select_dtypes(include=[np.number]).columns.difference(["target"])
    df[num_cols] = df[num_cols].fillna(df[num_cols].median())
    # Categorical columns → fill with mode
    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    for col in cat_cols:
        df[col].fillna(df[col].mode()[0], inplace=True)
    print("Imputed: numeric → median | categorical → mode")

# ==============================================================================
# 6. Separate Features and Target
# ==============================================================================
banner("6 · Feature / Target Split")

X = df.drop(columns=["target"])
y = df["target"]
print(f"X shape : {X.shape}")
print(f"y shape : {y.shape}   classes: {sorted(y.unique().tolist())}")

# ==============================================================================
# 7. One-Hot Encode Categorical Columns
# ==============================================================================
banner("7 · One-Hot Encoding")

cat_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
print(f"Encoding: {cat_cols}")
X = pd.get_dummies(X, columns=cat_cols, drop_first=False)
print(f"X shape after encoding: {X.shape}")

# ==============================================================================
# 8. Train / Test Split  (stratified to preserve class ratio in both halves)
# ==============================================================================
banner("8 · Train / Test Split")

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size    = TEST_SIZE,
    random_state = RANDOM_STATE,
    stratify     = y,           # keeps 98/2 ratio in both splits
)

print(f"Train : {len(X_train):,} samples  "
      f"(SAFE={int((y_train==0).sum()):,}  FAIL={int((y_train==1).sum()):,})")
print(f"Test  : {len(X_test):,}  samples  "
      f"(SAFE={int((y_test==0).sum()):,}   FAIL={int((y_test==1).sum()):,})")

# ==============================================================================
# 9. Oversample Minority Class — TRAINING SPLIT ONLY
#    Applying this to the test set would be data leakage.
# ==============================================================================
banner("9 · Minority Oversampling (train only)")

rng = np.random.default_rng(RANDOM_STATE)
X_train_res, y_train_res = oversample_minority(
    X_train.values, y_train.values, rng
)

safe_res = int((y_train_res == 0).sum())
fail_res = int((y_train_res == 1).sum())
print(f"Before : SAFE={int((y_train==0).sum()):,}  FAIL={int((y_train==1).sum()):,}")
print(f"After  : SAFE={safe_res:,}  FAIL={fail_res:,}")

# ==============================================================================
# 10. Train RandomForestClassifier
# ==============================================================================
banner("10 · Train RandomForestClassifier")

clf = RandomForestClassifier(
    n_estimators      = 300,        # more trees → smoother probabilities
    max_depth         = None,       # full-depth; leaf constraints prevent overfit
    min_samples_split = 5,
    min_samples_leaf  = 2,
    max_features      = "sqrt",     # standard for classification RF
    class_weight      = "balanced", # second layer of imbalance handling
    random_state      = RANDOM_STATE,
    n_jobs            = -1,         # use all available CPU cores
)

print("Training … ", end="", flush=True)
clf.fit(X_train_res, y_train_res)
print("done.")

# 5-fold stratified cross-validation (F1 on FAIL class)
cv    = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
cv_f1 = cross_val_score(clf, X_train_res, y_train_res,
                         cv=cv, scoring="f1", n_jobs=-1)
print(f"5-Fold CV F1 (train/resampled): {cv_f1.mean():.4f} ± {cv_f1.std():.4f}")

# ==============================================================================
# 11. Evaluate on the Held-Out Test Set
# ==============================================================================
banner("11 · Evaluation on Test Set")

y_pred      = clf.predict(X_test)
y_pred_prob = clf.predict_proba(X_test)[:, 1]   # P(FAIL)

accuracy  = accuracy_score (y_test, y_pred)
precision = precision_score(y_test, y_pred, zero_division=0)
recall    = recall_score   (y_test, y_pred, zero_division=0)
f1        = f1_score       (y_test, y_pred, zero_division=0)
roc_auc   = roc_auc_score  (y_test, y_pred_prob)

print(f"Accuracy  : {accuracy:.4f}")
print(f"Precision : {precision:.4f}  "
      "(of all drives flagged FAIL, how many truly are)")
print(f"Recall    : {recall:.4f}  "
      "(of all truly FAIL drives, how many we caught)")
print(f"F1-Score  : {f1:.4f}")
print(f"ROC-AUC   : {roc_auc:.4f}  (1.0 = perfect separator)")

print("\nClassification Report:")
print(classification_report(y_test, y_pred,
                             target_names=["SAFE", "FAIL"],
                             zero_division=0))

cm = confusion_matrix(y_test, y_pred)
tn, fp, fn, tp = cm.ravel()
print("Confusion Matrix  (rows = actual, cols = predicted):")
print(f"                 Pred SAFE   Pred FAIL")
print(f"  Actual SAFE       {tn:>5}       {fp:>5}")
print(f"  Actual FAIL       {fn:>5}       {tp:>5}")
if fn:
    print(f"\n  ↳  {fn} FAIL drive(s) missed (false negatives).")
    print("     For safety-critical use, lower the classification threshold.")

# ── Sanity checks ─────────────────────────────────────────────────────────────
unique_preds = np.unique(y_pred)
prob_min, prob_max = y_pred_prob.min(), y_pred_prob.max()
print()
if len(unique_preds) < 2:
    print("⚠  WARNING: model predicts only one class. "
          "Collect more failure samples or lower the decision threshold.")
else:
    print(f"✓  Model predicts BOTH classes: {unique_preds.tolist()}")
print(f"✓  FAIL probability range on test set: [{prob_min:.4f} … {prob_max:.4f}]")

# ── Top-10 Feature Importances ────────────────────────────────────────────────
print("\nTop-10 Feature Importances:")
importances = pd.Series(clf.feature_importances_, index=X_train.columns)
top10 = importances.sort_values(ascending=False).head(10)
for feat, imp in top10.items():
    bar = "█" * int(imp * 300)
    print(f"  {feat:<32s}  {imp:.4f}  {bar}")

# ==============================================================================
# 12. Save Model and Feature Column Names
# ==============================================================================
banner("12 · Save Artifacts")

# Column list from the original (pre-oversampling) training split.
# Oversampling only duplicates rows, not columns — either is fine here.
feature_columns = X_train.columns.tolist()

joblib.dump(clf,             MODEL_PATH)
joblib.dump(feature_columns, COLUMNS_PATH)

print(f"Model saved        → '{MODEL_PATH}'")
print(f"Feature cols saved → '{COLUMNS_PATH}'")
print(f"Total features     : {len(feature_columns)}")
banner()
print("✅  Training complete.  Run  python predict.py  to test inference.")
banner()
