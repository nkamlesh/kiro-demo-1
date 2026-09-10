"""Missing-value handling recommendations per column."""
from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd

from . import profiler


def _skew(series: pd.Series) -> float:
    s = series.dropna()
    if len(s) < 3:
        return 0.0
    try:
        return float(s.skew())
    except Exception:
        return 0.0


def recommend(df: pd.DataFrame, profiles: List[Dict], quality: Dict) -> List[Dict]:
    """Produce a per-column recommendation for handling missing values."""
    recs: List[Dict] = []
    for p in profiles:
        col = p["column"]
        col_type = p["type"]
        missing_pct = quality["missing"][col]["pct"]

        if missing_pct == 0:
            strategy = "No action needed"
            reason = "No missing values."
        elif missing_pct > 50:
            strategy = "Consider dropping column"
            reason = f"{missing_pct}% missing — too sparse to impute reliably."
        elif col_type == profiler.IDENTIFIER:
            strategy = "Do not impute — flag rows for review"
            reason = "Identifier columns must stay unique/valid."
        elif col_type == profiler.NUMERIC:
            sk = _skew(df[col])
            if abs(sk) > 1:
                strategy = "Median imputation"
                reason = f"Skewed distribution (skew={sk:.2f}); median is robust to outliers."
            else:
                strategy = "Mean imputation"
                reason = f"Roughly symmetric (skew={sk:.2f}); mean is appropriate."
        elif col_type in (profiler.CATEGORICAL, profiler.BOOLEAN):
            strategy = "Mode imputation or 'Unknown' category"
            reason = "Low-cardinality column; fill with most frequent value or an explicit 'Unknown'."
        elif col_type == profiler.DATETIME:
            strategy = "Forward-fill / interpolate"
            reason = "Time-series-like data; carry last value forward or interpolate."
        else:  # free-form text
            strategy = "Fill with 'Unknown' or leave blank"
            reason = "Free-form text; imputation rarely meaningful."

        recs.append(
            {
                "column": col,
                "type": col_type,
                "missing_pct": missing_pct,
                "strategy": strategy,
                "reason": reason,
            }
        )
    return recs
