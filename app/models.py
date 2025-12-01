from typing import Tuple, Dict, Any
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import numpy as np


def get_model(name: str, params: Dict[str, Any] = None):
    params = params or {}
    if name == "LogisticRegression":
        return LogisticRegression(solver="liblinear", **params)
    if name == "RandomForest":
        return RandomForestClassifier(n_jobs=-1, **params)
    raise ValueError(f"Unknown model: {name}")


def train_and_evaluate(model, X_train, X_test, y_train, y_test) -> Tuple[object, dict]:
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    proba = None
    try:
        proba = model.predict_proba(X_test)[:, 1]
    except Exception:
        proba = None

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, preds)), 4),
        "precision": round(float(precision_score(y_test, preds, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, preds, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, preds, zero_division=0)), 4),
    }
    if proba is not None and len(np.unique(y_test)) == 2:
        try:
            metrics["roc_auc"] = round(float(roc_auc_score(y_test, proba)), 4)
        except Exception:
            metrics["roc_auc"] = None

    return model, metrics
