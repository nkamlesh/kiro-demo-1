"""Data quality checks: missing values, duplicates, outliers, constant columns."""
from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd

from . import profiler


def _outlier_count_iqr(series: pd.Series) -> int:
    """Count outliers in a numeric series using the IQR method."""
    s = series.dropna()
    if len(s) < 4:
        return 0
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        return 0
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return int(((s < lower) | (s > upper)).sum())


def _mixed_type_columns(df: pd.DataFrame) -> List[str]:
    """Detect object columns that contain more than one Python scalar type."""
    mixed = []
    for col in df.columns:
        if df[col].dtype == object:
            types = df[col].dropna().map(type).nunique()
            if types > 1:
                mixed.append(col)
    return mixed


def run_quality_checks(df: pd.DataFrame, profiles: List[Dict]) -> Dict:
    """Compute the full data-quality report as a serialisable dict."""
    total = len(df)
    type_by_col = {p["column"]: p["type"] for p in profiles}

    missing = {
        col: {
            "count": int(df[col].isna().sum()),
            "pct": round(df[col].isna().sum() / total * 100, 2) if total else 0.0,
        }
        for col in df.columns
    }

    outliers = {}
    for col in df.columns:
        if type_by_col.get(col) == profiler.NUMERIC:
            outliers[col] = _outlier_count_iqr(df[col])

    constant_cols = [c for c in df.columns if df[c].nunique(dropna=True) <= 1]
    high_missing = [c for c, m in missing.items() if m["pct"] > 50]

    return {
        "n_rows": total,
        "n_cols": df.shape[1],
        "duplicate_rows": int(df.duplicated().sum()),
        "total_missing_cells": int(df.isna().sum().sum()),
        "missing": missing,
        "outliers": outliers,
        "constant_columns": constant_cols,
        "high_missing_columns": high_missing,
        "mixed_type_columns": _mixed_type_columns(df),
    }
