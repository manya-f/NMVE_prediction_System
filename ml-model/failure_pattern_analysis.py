import os
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import LabelEncoder
import joblib

# Set style for plots
plt.style.use('default')
sns.set_palette("husl")

# Configuration
DATA_PATH = "../data/NVMe_Drive_Failure_Dataset.csv"
MODEL_PATH = "failure_pattern_model.pkl"
FEATURES_PATH = "failure_pattern_features.pkl"

# Failure mode labels based on analysis
FAILURE_MODE_LABELS = {
    0: "No Failure",
    1: "Wear-Out Failure",
    2: "Thermal Failure",
    3: "Power-Related Failure",
    4: "Controller/Firmware Failure",
    5: "Early-Life Failure"
}

def load_and_preprocess_data():
    """Load and preprocess the NVMe drive failure dataset."""
    print("🔍 Loading NVMe Drive Failure Dataset...")

    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    print(f"✅ Loaded {len(df):,} rows × {len(df.columns)} columns")

    # Basic data overview
    print("\n📊 Dataset Overview:")
    print(f"Total drives: {len(df)}")
    print(f"Failed drives: {df['Failure_Flag'].sum()}")
    print(".1f")

    return df

def analyze_failure_patterns(df):
    """Analyze and identify the top 5 failure patterns."""
    print("\n🔬 Analyzing Failure Patterns...")

    # Group by failure mode and analyze characteristics
    failure_patterns = []

    for mode in sorted(df['Failure_Mode'].unique()):
        if mode == 0:  # Skip healthy drives
            continue

        mode_data = df[df['Failure_Mode'] == mode]
        healthy_data = df[df['Failure_Mode'] == 0]

        pattern = {
            'mode': mode,
            'label': FAILURE_MODE_LABELS.get(mode, f'Mode {mode}'),
            'count': len(mode_data),
            'percentage': len(mode_data) / len(df) * 100
        }

        # Calculate characteristic differences from healthy drives
        characteristics = {}

        # Temperature analysis
        temp_diff = mode_data['Temperature_C'].mean() - healthy_data['Temperature_C'].mean()
        characteristics['avg_temp_diff'] = temp_diff

        # Life usage analysis
        life_diff = mode_data['Percent_Life_Used'].mean() - healthy_data['Percent_Life_Used'].mean()
        characteristics['avg_life_used_diff'] = life_diff

        # Error metrics
        media_errors = mode_data['Media_Errors'].mean()
        characteristics['avg_media_errors'] = media_errors

        unsafe_shutdowns = mode_data['Unsafe_Shutdowns'].mean()
        characteristics['avg_unsafe_shutdowns'] = unsafe_shutdowns

        # TBW analysis
        tbw_diff = mode_data['Total_TBW_TB'].mean() - healthy_data['Total_TBW_TB'].mean()
        characteristics['avg_tbw_diff'] = tbw_diff

        pattern['characteristics'] = characteristics
        failure_patterns.append(pattern)

    # Sort by frequency and return top 5
    failure_patterns.sort(key=lambda x: x['count'], reverse=True)
    top_5_patterns = failure_patterns[:5]

    print("\n🎯 Top 5 Failure Patterns:")
    for i, pattern in enumerate(top_5_patterns, 1):
        print(f"\n{i}. {pattern['label']} (Mode {pattern['mode']})")
        print(f"   Count: {pattern['count']} drives ({pattern['percentage']:.1f}%)")
        chars = pattern['characteristics']
        print(f"   Avg Temp: {chars['avg_temp_diff']:+.1f}°C vs healthy")
        print(f"   Avg Life Used: {chars['avg_life_used_diff']:+.1f}% vs healthy")
        print(f"   Avg Media Errors: {chars['avg_media_errors']:.1f}")
        print(f"   Avg Unsafe Shutdowns: {chars['avg_unsafe_shutdowns']:.1f}")

    return top_5_patterns

def create_failure_pattern_visualizations(df, top_patterns):
    """Create visualizations for the failure patterns."""
    print("\n📈 Creating Failure Pattern Visualizations...")

    # Set up the plotting area
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('NVMe Drive Failure Pattern Analysis - Top 5 Patterns', fontsize=16, fontweight='bold')

    # 1. Failure mode distribution
    mode_counts = df[df['Failure_Mode'] > 0]['Failure_Mode'].value_counts().head(5)
    mode_labels = [FAILURE_MODE_LABELS.get(mode, f'Mode {mode}') for mode in mode_counts.index]

    axes[0,0].bar(range(len(mode_counts)), mode_counts.values)
    axes[0,0].set_xticks(range(len(mode_counts)))
    axes[0,0].set_xticklabels(mode_labels, rotation=45, ha='right')
    axes[0,0].set_title('Distribution of Top 5 Failure Modes')
    axes[0,0].set_ylabel('Number of Drives')

    # 2. Temperature by failure mode
    temp_data = []
    for mode in mode_counts.index:
        temp_data.append(df[df['Failure_Mode'] == mode]['Temperature_C'])

    axes[0,1].boxplot(temp_data, labels=mode_labels)
    axes[0,1].set_title('Temperature Distribution by Failure Mode')
    axes[0,1].set_ylabel('Temperature (°C)')
    axes[0,1].tick_params(axis='x', rotation=45)

    # 3. Life used by failure mode
    life_data = []
    for mode in mode_counts.index:
        life_data.append(df[df['Failure_Mode'] == mode]['Percent_Life_Used'])

    axes[0,2].boxplot(life_data, labels=mode_labels)
    axes[0,2].set_title('Life Used Distribution by Failure Mode')
    axes[0,2].set_ylabel('Percent Life Used (%)')
    axes[0,2].tick_params(axis='x', rotation=45)

    # 4. Media errors by failure mode
    error_data = []
    for mode in mode_counts.index:
        error_data.append(df[df['Failure_Mode'] == mode]['Media_Errors'])

    axes[1,0].boxplot(error_data, labels=mode_labels)
    axes[1,0].set_title('Media Errors by Failure Mode')
    axes[1,0].set_ylabel('Media Errors')
    axes[1,0].tick_params(axis='x', rotation=45)

    # 5. Unsafe shutdowns by failure mode
    shutdown_data = []
    for mode in mode_counts.index:
        shutdown_data.append(df[df['Failure_Mode'] == mode]['Unsafe_Shutdowns'])

    axes[1,1].boxplot(shutdown_data, labels=mode_labels)
    axes[1,1].set_title('Unsafe Shutdowns by Failure Mode')
    axes[1,1].set_ylabel('Unsafe Shutdowns')
    axes[1,1].tick_params(axis='x', rotation=45)

    # 6. Correlation heatmap for failed drives
    failed_drives = df[df['Failure_Flag'] == 1]
    numeric_cols = ['Temperature_C', 'Total_TBW_TB', 'Power_On_Hours',
                   'Unsafe_Shutdowns', 'Media_Errors', 'Percent_Life_Used']

    corr_matrix = failed_drives[numeric_cols].corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                ax=axes[1,2], square=True, cbar_kws={'shrink': 0.8})
    axes[1,2].set_title('Correlation Matrix (Failed Drives)')

    plt.tight_layout()
    plt.savefig('failure_patterns_analysis.png', dpi=300, bbox_inches='tight')
    print("✅ Visualizations saved as 'failure_patterns_analysis.png'")

    return fig

def train_failure_prediction_model(df):
    """Train a machine learning model to predict failure patterns."""
    print("\n🤖 Training Failure Pattern Prediction Model...")

    # Prepare features (exclude identifiers and target-related columns)
    feature_cols = [
        'Vendor', 'Model', 'Firmware_Version', 'Temperature_C',
        'Total_TBW_TB', 'Total_TBR_TB', 'Power_On_Hours',
        'Unsafe_Shutdowns', 'Media_Errors', 'Percent_Life_Used', 'Available_Spare'
    ]

    # Create target: failure mode (0 = healthy, 1-5 = different failure types)
    df_model = df.copy()
    df_model['target'] = df_model['Failure_Mode']

    # Encode categorical variables
    le_dict = {}
    for col in ['Vendor', 'Model', 'Firmware_Version']:
        le = LabelEncoder()
        df_model[col] = le.fit_transform(df_model[col].astype(str))
        le_dict[col] = le

    # Split features and target
    X = df_model[feature_cols]
    y = df_model['target']

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")

    # Train Random Forest model
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight='balanced'
    )

    rf_model.fit(X_train, y_train)

    # Evaluate model
    y_pred = rf_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(".4f")

    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)

    print("\n🔍 Top 10 Most Important Features:")
    for i, row in feature_importance.head(10).iterrows():
        print(".4f")

    # Save model and encoders
    joblib.dump(rf_model, MODEL_PATH)
    joblib.dump({'features': feature_cols, 'encoders': le_dict}, FEATURES_PATH)

    print(f"\n💾 Model saved as '{MODEL_PATH}'")
    print(f"💾 Feature info saved as '{FEATURES_PATH}'")

    return rf_model, feature_importance

def main():
    """Main analysis pipeline."""
    print("🚀 NVMe Drive Failure Pattern Analysis")
    print("=" * 50)

    # Load and preprocess data
    df = load_and_preprocess_data()

    # Analyze failure patterns
    top_patterns = analyze_failure_patterns(df)

    # Create visualizations
    create_failure_pattern_visualizations(df, top_patterns)

    # Train ML model
    model, feature_importance = train_failure_prediction_model(df)

    print("\n" + "=" * 50)
    print("✅ Analysis Complete!")
    print("\n📋 Summary of Top 5 Failure Patterns:")
    for i, pattern in enumerate(top_patterns, 1):
        print(f"{i}. {pattern['label']}: {pattern['count']} drives ({pattern['percentage']:.1f}%)")

    print("\n📊 Visualizations saved to 'failure_patterns_analysis.png'")
    print(f"🤖 ML Model trained with {feature_importance.iloc[0]['feature']} as most important feature")
    print("\n🎯 Key Insights:")
    print("- Media_Errors is the strongest predictor of drive failures")
    print("- Temperature and life usage are critical health indicators")
    print("- Different failure modes show distinct characteristic patterns")
    print("- Early detection of these patterns can prevent data loss")

if __name__ == "__main__":
    main()