import joblib
from typing import Any
import io


def save_model_to_bytes(model: Any) -> bytes:
    buf = io.BytesIO()
    joblib.dump(model, buf)
    buf.seek(0)
    return buf.read()


def save_model_to_path(model: Any, path: str):
    joblib.dump(model, path)


def load_model_from_path(path: str):
    return joblib.load(path)
