import os
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)

from preprocess import (
    load_dataset,
    clean_dataset,
    prepare_feature_matrix,
    build_preprocessor,
    SELECTED_FEATURES,
)

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
IMPORTANCE_PATH = os.path.join(MODEL_DIR, "feature_importance.png")
DATA_PATH = os.path.join(BASE_DIR, "data", "NVMe_Drive_Failure_Dataset.csv")

FAILURE_MODE_LABELS = {
    0: "Healthy",
    1: "Wear-Out Failure",
    2: "Thermal Failure",
    3: "Power-Related Failure",
    4: "Controller/Firmware Failure",
    5: "Early-Life Failure",
}


def evaluate_model(name, pipeline, X_test, y_test):
    """Evaluate a trained pipeline and print key metrics."""
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    pr = precision_score(y_test, y_pred)
    rc = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    print(f"\n{name} Evaluation")
    print("---------------------------")
    print(f"Accuracy : {acc:.4f}")
    print(f"Precision: {pr:.4f}")
    print(f"Recall   : {rc:.4f}")
    print(f"F1-score : {f1:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Healthy", "Failing"]))

    return {
        "name": name,
        "accuracy": acc,
        "precision": pr,
        "recall": rc,
        "f1": f1,
        "pipeline": pipeline,
    }


def plot_feature_importance(model, feature_names, output_path):
    """Save a bar chart showing feature importance from Random Forest."""
    importances = model.feature_importances_
    feature_importance = pd.Series(importances, index=feature_names).sort_values(ascending=False)

    plt.figure(figsize=(8, 5))
    sns.barplot(x=feature_importance.values, y=feature_importance.index, palette="viridis")
    plt.title("Feature Importance - Random Forest")
    plt.xlabel("Importance")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"✅ Saved feature importance visualization to {output_path}")


def analyze_failure_patterns(df):
    """Analyze Failure_Mode patterns and print the top causes."""
    print("\n📊 Failure Mode Pattern Analysis")
    print("-------------------------------")

    pattern_stats = (
        df.groupby("Failure_Mode")
        .agg(
            count=("Failure_Flag", "size"),
            avg_temperature=("Temperature_C", "mean"),
            avg_shutdowns=("Unsafe_Shutdowns", "mean"),
            avg_media_errors=("Media_Errors", "mean"),
            avg_life_used=("Percent_Life_Used", "mean"),
        )
        .reset_index()
    )

    pattern_stats = pattern_stats.sort_values(by="count", ascending=False)
    pattern_stats["mode_label"] = pattern_stats["Failure_Mode"].map(FAILURE_MODE_LABELS)

    top_patterns = pattern_stats[pattern_stats["Failure_Mode"] != 0].head(5)
    for _, row in top_patterns.iterrows():
        print(f"\nFailure Mode {int(row['Failure_Mode'])}: {row['mode_label']}")
        print(f"  Count          : {int(row['count'])}")
        print(f"  Avg Temp       : {row['avg_temperature']:.1f}°C")
        print(f"  Avg Shutdowns  : {row['avg_shutdowns']:.1f}")
        print(f"  Avg Media Errs : {row['avg_media_errors']:.1f}")
        print(f"  Avg Life Used  : {row['avg_life_used']:.1f}%")

    print("\nTop 5 failure patterns identified by failure mode counts.")
    return top_patterns


def build_pipeline(model):
    """Build a preprocessing + model pipeline."""
    preprocessor = build_preprocessor()
    from sklearn.pipeline import Pipeline
    pipeline = Pipeline(
        [
            ("preprocessor", preprocessor),
            ("classifier", model),
        ]
    )
    return pipeline


def main():
    print("=====================\nNVMe SMART Prediction Training\n=====================")

    df = load_dataset(DATA_PATH)
    df = clean_dataset(df)
    X, y = prepare_feature_matrix(df)

    print(f"Loaded dataset with {len(df):,} rows")
    print("Selected features:", SELECTED_FEATURES)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    models = {
        "Logistic Regression": LogisticRegression(
            solver="liblinear",
            class_weight="balanced",
            random_state=42,
            max_iter=500,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),
    }

    if XGBOOST_AVAILABLE:
        models["XGBoost"] = XGBClassifier(
            use_label_encoder=False,
            eval_metric="logloss",
            n_estimators=150,
            learning_rate=0.1,
            random_state=42,
            verbosity=0,
        )

    evaluations = []
    for name, model in models.items():
        pipeline = build_pipeline(model)
        pipeline.fit(X_train, y_train)
        evaluations.append(evaluate_model(name, pipeline, X_test, y_test))

    best = max(evaluations, key=lambda item: item["f1"])
    best_model = best["pipeline"]
    print(f"\n✅ Best model: {best['name']} with F1 {best['f1']:.4f}")

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(best_model, MODEL_PATH)
    print(f"✅ Saved best model to {MODEL_PATH}")

    if "Random Forest" in models:
        rf_pipeline = build_pipeline(models["Random Forest"])
        rf_pipeline.fit(X_train, y_train)
        rf_model = rf_pipeline.named_steps["classifier"]
        plot_feature_importance(rf_model, SELECTED_FEATURES, IMPORTANCE_PATH)

    analyze_failure_patterns(df)

    cm = confusion_matrix(y_test, best_model.predict(X_test))
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["Healthy", "Failing"], yticklabels=["Healthy", "Failing"])
    plt.ylabel("Actual")
    plt.xlabel("Predicted")
    plt.title("Confusion Matrix")
    plt.tight_layout()
    confusion_path = os.path.join(MODEL_DIR, "confusion_matrix.png")
    plt.savefig(confusion_path, dpi=200)
    plt.close()
    print(f"✅ Saved confusion matrix to {confusion_path}")


if __name__ == "__main__":
    main()
