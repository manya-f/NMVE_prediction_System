from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split


DATA_FILE = Path(__file__).with_name("NVMe_Drive_Failure_Dataset.csv")
FAILURE_LABELS = {0: "Healthy", 1: "Failed"}
FAILURE_MODE_LABELS = {
    0: "No Failure",
    1: "Controller Fault",
    4: "Thermal Issue",
    5: "Wear Out",
}
PAIRPLOT_COLUMNS = [
    "Temperature_C",
    "Percent_Life_Used",
    "Media_Errors",
    "Read_Error_Rate",
    "Failure_Label",
]


def configure_style() -> None:
    sns.set_theme(style="darkgrid", palette="Set2")
    plt.rcParams["figure.figsize"] = (10, 6)


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE)
    df["Failure_Label"] = df["Failure_Flag"].map(FAILURE_LABELS)
    df["Failure_Mode_Label"] = df["Failure_Mode"].map(FAILURE_MODE_LABELS).fillna("Other")
    return df


def print_overview(df: pd.DataFrame) -> None:
    print("\nHead:")
    print(df.head())
    print("\nInfo:")
    df.info()
    print("\nDescribe:")
    print(df.describe())
    print("\nMissing values:")
    print(df.isnull().sum())
    print("\nFailure counts:")
    print(df["Failure_Label"].value_counts())
    print("\nFailure mode counts:")
    print(df["Failure_Mode_Label"].value_counts())
    print("\nGroup means by failure flag:")
    print(df.groupby("Failure_Flag").mean(numeric_only=True))


def print_key_insights(df: pd.DataFrame) -> None:
    failure_rate = df["Failure_Flag"].mean() * 100
    print("\nKEY INSIGHTS:")
    print(f"- Failure rate is low ({failure_rate:.2f}%), indicating class imbalance.")
    print("- SMART Warning Flag is highly correlated with failures.")
    print("- Error metrics (media, read/write) are strong indicators of failure.")
    print("- Higher temperature contributes to thermal stress.")
    print("- Higher life usage indicates wear-out failures.")


def plot_failure_distribution(df: pd.DataFrame) -> None:
    counts = df["Failure_Label"].value_counts()
    ax = sns.countplot(data=df, x="Failure_Label", palette=["green", "red"])
    plt.title("Failure vs Healthy Drives")
    plt.xlabel("Drive Status")
    plt.ylabel("Count")
    for i, v in enumerate(counts):
        percentage = (v / len(df)) * 100
        ax.text(i, v + 50, f"{percentage:.2f}%", ha="center")
    plt.tight_layout()
    plt.show()


def plot_dashboard(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    sns.boxplot(data=df, x="Failure_Label", y="Temperature_C", ax=axes[0, 0])
    axes[0, 0].set_title("Temperature vs Failure")
    axes[0, 0].axhline(50, color="red", linestyle="--", label="High Temp Threshold (50C)")
    axes[0, 0].legend()

    sns.boxplot(data=df, x="Failure_Label", y="Percent_Life_Used", ax=axes[0, 1])
    axes[0, 1].set_title("Life Used vs Failure")

    sns.boxplot(data=df, x="Failure_Label", y="Media_Errors", ax=axes[1, 0])
    axes[1, 0].set_title("Media Errors vs Failure")

    sns.boxplot(data=df, x="Failure_Mode_Label", y="Temperature_C", ax=axes[1, 1])
    axes[1, 1].set_title("Temperature vs Failure Mode")
    axes[1, 1].tick_params(axis="x", rotation=15)

    fig.tight_layout()
    plt.show()


def plot_detailed_analysis(df: pd.DataFrame) -> None:
    sns.violinplot(data=df, x="Failure_Label", y="Temperature_C")
    plt.title("Temperature Distribution by Failure")
    plt.axhline(50, color="red", linestyle="--", label="High Temp Threshold (50C)")
    plt.legend()
    plt.tight_layout()
    plt.show()

    failed = df[df["Failure_Label"] == "Failed"]
    healthy = df[df["Failure_Label"] == "Healthy"].sample(min(500, (df["Failure_Label"] == "Healthy").sum()), random_state=42)
    sns.kdeplot(data=healthy, x="Temperature_C", fill=True, label="Healthy (sample)", color="green")
    sns.kdeplot(data=failed, x="Temperature_C", fill=True, label="Failed", color="red")
    plt.title("Temperature Density (Balanced View)")
    plt.tight_layout()
    plt.legend()
    plt.show()

    sns.boxplot(data=df, x="Failure_Label", y="Power_On_Hours")
    plt.title("Usage Hours vs Failure")
    plt.tight_layout()
    plt.show()

    for column, title in [
        ("Media_Errors", "Media Errors vs Failure"),
        ("Unsafe_Shutdowns", "Unsafe Shutdowns vs Failure"),
        ("Read_Error_Rate", "Read Error Rate vs Failure"),
        ("Write_Error_Rate", "Write Error Rate vs Failure"),
    ]:
        sns.boxplot(data=df, x="Failure_Label", y=column)
        plt.title(title)
        plt.tight_layout()
        plt.show()

    plt.figure(figsize=(12, 8))
    corr = df.corr(numeric_only=True)
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.show()
    corr_target = corr["Failure_Flag"].drop("Failure_Flag").sort_values(ascending=False)
    print("\nTop Factors Affecting Failure:")
    print(corr_target.head(5))

    top_features = corr_target.head(5)
    sns.barplot(x=top_features.values, y=top_features.index)
    plt.title("Top Features Influencing Failure")
    plt.xlabel("Correlation with Failure")
    plt.tight_layout()
    plt.show()

    df_sample = df.sample(min(1000, len(df)), random_state=42)
    sns.scatterplot(
        data=df_sample,
        x="Power_On_Hours",
        y="Temperature_C",
        hue="Failure_Label",
        alpha=0.7,
    )
    plt.title("Usage vs Temperature vs Failure")
    plt.tight_layout()
    plt.show()

    failed_df = df[df["Failure_Label"] == "Failed"]
    sns.countplot(data=failed_df, x="Failure_Mode_Label", hue="Failure_Mode_Label", legend=False, palette="Set1")
    plt.title("Failure Mode Distribution (Failed Drives Only)")
    plt.xlabel("Failure Mode")
    plt.ylabel("Count")
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.show()

    sample_size = min(500, len(df))
    sns.pairplot(
        df[PAIRPLOT_COLUMNS].sample(sample_size, random_state=42),
        hue="Failure_Label",
        corner=True,
    )
    plt.show()


def plot_interactive_chart(df: pd.DataFrame) -> None:
    fig = px.scatter(
        df,
        x="Power_On_Hours",
        y="Temperature_C",
        color="Failure_Label",
        hover_data=["Vendor", "Model", "Failure_Mode_Label"],
        title="Interactive: Usage vs Temperature vs Failure",
    )
    fig.show()


def run_simple_model(df: pd.DataFrame) -> None:
    features = [
        "Temperature_C",
        "Percent_Life_Used",
        "Media_Errors",
        "Read_Error_Rate",
        "Write_Error_Rate",
        "SMART_Warning_Flag",
    ]
    X = df[features]
    y = df["Failure_Flag"]
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )
    model = RandomForestClassifier(class_weight="balanced", random_state=42)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    report = classification_report(y_test, predictions, output_dict=True)
    accuracy = (predictions == y_test).mean()
    print("\nMODEL PERFORMANCE:")
    print(pd.DataFrame(report).transpose())
    print(f"\nModel Accuracy: {accuracy:.4f}")

    cm = confusion_matrix(y_test, predictions)
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Healthy", "Failed"],
        yticklabels=["Healthy", "Failed"],
    )
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    plt.show()

    feature_importance = pd.Series(
        model.feature_importances_,
        index=features,
    ).sort_values(ascending=False)
    print("\nFeature Importance:")
    print(feature_importance)

    feature_importance = feature_importance.sort_values(ascending=True)
    sns.barplot(x=feature_importance.values, y=feature_importance.index)
    plt.title("Feature Importance (Model Insight)")
    plt.xlabel("Importance Score")
    plt.tight_layout()
    plt.show()

    print("\nNOTE: Due to class imbalance, accuracy alone is not sufficient. Precision and recall are more important.")


def main() -> None:
    configure_style()
    df = load_data()
    print_overview(df)
    print_key_insights(df)
    plot_failure_distribution(df)
    plot_dashboard(df)
    plot_detailed_analysis(df)
    plot_interactive_chart(df)
    run_simple_model(df)
    print("\nFINAL CONCLUSION:")
    print("1. Failure is rare but predictable using SMART metrics.")
    print("2. SMART Warning Flag is the strongest indicator.")
    print("3. Error rates significantly increase before failure.")
    print("4. Temperature contributes to thermal stress.")
    print("5. Life usage reflects wear-out failures.")


if __name__ == "__main__":
    main()
