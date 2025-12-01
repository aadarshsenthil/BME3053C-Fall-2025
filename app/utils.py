import pandas as pd
from pathlib import Path
import io
from typing import Tuple, Optional


def list_workspace_csvs(root: str = ".") -> list:
    p = Path(root) / "files"
    if not p.exists():
        return []
    return sorted([str(x) for x in p.glob("*.csv")])


def load_csv(path_or_buffer, nrows: Optional[int] = None) -> pd.DataFrame:
    """Load CSV from a file path (workspace) or an uploaded buffer (Streamlit)."""
    # If it's a path string
    if isinstance(path_or_buffer, str):
        try:
            return pd.read_csv(path_or_buffer, engine="python")
        except Exception:
            # try with default separators
            return pd.read_csv(path_or_buffer)

    # Otherwise assume it's a buffer (like UploadedFile)
    if hasattr(path_or_buffer, "read"):
        data = path_or_buffer.read()
        if isinstance(data, bytes):
            data = data.decode("utf-8", errors="ignore")
        return pd.read_csv(io.StringIO(data))

    raise ValueError("Unsupported input for load_csv")


def preview_dataframe(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    return df.head(n)


def infer_target_column(df: pd.DataFrame) -> Optional[str]:
    """Try to infer a sensible target column (heuristics)."""
    candidates = [
        c for c in ["target", "label", "y", "cardio", "outcome"] if c in df.columns
    ]
    if candidates:
        return candidates[0]
    # fallback: look for binary-int column
    for c in df.columns:
        unique = df[c].dropna().unique()
        if len(unique) == 2:
            return c
    return None
