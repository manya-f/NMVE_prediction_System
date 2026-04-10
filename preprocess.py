import os
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "NVMe_Drive_Failure_Dataset.csv")

# Use the SMART metrics that match the requested single-input interface.
SELECTED_FEATURES = [
    "Temperature_C",
    "Power_On_Hours",
    "Percent_Life_Used",
    "Unsafe_Shutdowns",
    "Media_Errors"
]
TARGET_COLUMN = "Failure_Flag"


def load_dataset(path: str = DATA_PATH) -> pd.DataFrame:
    """Load the NVMe dataset from the data folder."""
    df = pd.read_csv(path)
    return df


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Handle missing values and clean the dataset."""
    df = df.copy()
    df = df.drop_duplicates(subset=["Drive_ID"])

    numeric_columns = SELECTED_FEATURES
    df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())

    # If a required value is still missing, fill with 0 as a safe fallback.
    df[numeric_columns] = df[numeric_columns].fillna(0)
    return df


def prepare_feature_matrix(df: pd.DataFrame):
    """Extract the training matrix and target vector."""
    X = df[SELECTED_FEATURES].astype(float)
    y = df[TARGET_COLUMN].astype(int)
    return X, y


def build_preprocessor() -> Pipeline:
    """Create a preprocessing pipeline for numeric SMART inputs."""
    numeric_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ]
    )
    return numeric_pipeline
