from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from typing import List


def build_preprocessor(numeric_cols: List[str], categorical_cols: List[str],
                       scaler: str = "standard", impute_strategy: str = "mean") -> ColumnTransformer:
    """Return a ColumnTransformer for numeric and categorical preprocessing."""
    if scaler == "standard":
        scaler_obj = StandardScaler()
    elif scaler == "robust":
        scaler_obj = RobustScaler()
    else:
        scaler_obj = MinMaxScaler()

    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy=impute_strategy)),
        ("scaler", scaler_obj),
    ])

    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse=False)),
    ])

    return ColumnTransformer([
        ("num", numeric_pipeline, numeric_cols),
        ("cat", categorical_pipeline, categorical_cols),
    ], remainder="drop")
