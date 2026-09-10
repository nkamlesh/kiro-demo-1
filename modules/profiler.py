"""Column type detection and profiling."""
from __future__ import annotations

from typing import Dict, List

import pandas as pd
from pandas.api import types as ptypes


# Column type constants
NUMERIC = "numeric"
CATEGORICAL = "categorical"
DATETIME = "datetime"
BOOLEAN = "boolean"
TEXT = "text/free-form"
IDENTIFIER = "identifier"


def classify_column(series: pd.Series, name: str) -> str:
    """Classify a single column into one of the semantic types."""
    non_null = series.dropna()
    n = len(series)

    if ptypes.is_bool_dtype(series):
        return BOOLEAN
    if ptypes.is_datetime64_any_dtype(series):
        return DATETIME

    if ptypes.is_numeric_dtype(series):
        # Numeric columns that look like unique IDs.
        if _looks_like_identifier(series, name):
            return IDENTIFIER
        return NUMERIC

    # Object / string columns: try datetime parsing first.
    if len(non_null) > 0:
        parsed = pd.to_datetime(non_null, errors="coerce")
        if parsed.notna().mean() >= 0.9:
            return DATETIME

    if _looks_like_identifier(series, name):
        return IDENTIFIER

    # Low-cardinality object columns -> categorical, else free-form text.
    unique_ratio = series.nunique(dropna=True) / max(n, 1)
    if series.nunique(dropna=True) <= 20 or unique_ratio <= 0.5:
        return CATEGORICAL
    return TEXT


def _looks_like_identifier(series: pd.Series, name: str) -> bool:
    """Heuristic: near-unique values and/or an id-like column name."""
    n = len(series)
    if n == 0:
        return False
    name_l = str(name).lower()
    name_hit = any(
        tok in name_l for tok in ("id", "uuid", "guid", "code", "key", "number", "no.")
    )
    unique_ratio = series.nunique(dropna=True) / n
    if unique_ratio >= 0.95 and (name_hit or not ptypes.is_float_dtype(series)):
        return True
    return False


def profile_columns(df: pd.DataFrame) -> List[Dict]:
    """Build a per-column profile with type, missing %, unique count, samples."""
    total = len(df)
    profiles: List[Dict] = []
    for col in df.columns:
        series = df[col]
        col_type = classify_column(series, col)
        missing = int(series.isna().sum())
        missing_pct = round((missing / total * 100), 2) if total else 0.0
        samples = (
            series.dropna().astype(str).unique()[:3].tolist()
            if series.notna().any()
            else []
        )
        profiles.append(
            {
                "column": col,
                "type": col_type,
                "dtype": str(series.dtype),
                "unique": int(series.nunique(dropna=True)),
                "missing": missing,
                "missing_pct": missing_pct,
                "samples": ", ".join(samples),
            }
        )
    return profiles


def columns_by_type(profiles: List[Dict]) -> Dict[str, List[str]]:
    """Group column names by semantic type."""
    grouped: Dict[str, List[str]] = {}
    for p in profiles:
        grouped.setdefault(p["type"], []).append(p["column"])
    return grouped
