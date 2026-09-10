"""Chart engine: auto-selects chart types per column and returns base64 PNGs.

Uses a non-interactive matplotlib backend so it works headless (inside
Streamlit and in the exported HTML report).
"""
from __future__ import annotations

import base64
import io
from typing import Dict, List

import matplotlib

matplotlib.use("Agg")  # headless backend — must be set before pyplot import
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

try:
    import seaborn as sns  # noqa: E402

    sns.set_theme(style="whitegrid")
    _HAS_SEABORN = True
except Exception:  # pragma: no cover - seaborn optional
    _HAS_SEABORN = False

from . import profiler  # noqa: E402


# Caps to avoid generating hundreds of charts on wide files.
MAX_NUMERIC = 8
MAX_CATEGORICAL = 8


def _fig_to_base64(fig) -> str:
    """Encode a matplotlib figure as a base64 PNG data string."""
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=90, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def _numeric_chart(series: pd.Series, name: str) -> str:
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.2))
    data = series.dropna()
    axes[0].hist(data, bins=min(30, max(5, int(np.sqrt(len(data)) or 5))),
                 color="#4C78A8", edgecolor="white")
    axes[0].set_title(f"Distribution of {name}")
    axes[0].set_xlabel(name)
    axes[0].set_ylabel("Count")
    axes[1].boxplot(data, vert=True, patch_artist=True,
                    boxprops=dict(facecolor="#9ECAE9"))
    axes[1].set_title(f"Boxplot of {name}")
    axes[1].set_ylabel(name)
    return _fig_to_base64(fig)


def _categorical_chart(series: pd.Series, name: str) -> str:
    counts = series.astype(str).value_counts().head(10)
    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.barh(counts.index[::-1], counts.values[::-1], color="#54A24B")
    ax.set_title(f"Top categories in {name}")
    ax.set_xlabel("Count")
    return _fig_to_base64(fig)


def _correlation_heatmap(df: pd.DataFrame, numeric_cols: List[str]) -> str:
    corr = df[numeric_cols].corr(numeric_only=True)
    fig, ax = plt.subplots(figsize=(min(1 + len(numeric_cols), 9),
                                    min(1 + len(numeric_cols), 8)))
    if _HAS_SEABORN:
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
                    vmin=-1, vmax=1, ax=ax, cbar=True)
    else:
        im = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
        ax.set_xticks(range(len(numeric_cols)))
        ax.set_yticks(range(len(numeric_cols)))
        ax.set_xticklabels(numeric_cols, rotation=45, ha="right")
        ax.set_yticklabels(numeric_cols)
        fig.colorbar(im, ax=ax)
    ax.set_title("Correlation heatmap")
    return _fig_to_base64(fig)


def _datetime_trend(df: pd.DataFrame, date_col: str, num_col: str) -> str:
    tmp = df[[date_col, num_col]].dropna().copy()
    tmp[date_col] = pd.to_datetime(tmp[date_col], errors="coerce")
    tmp = tmp.dropna().sort_values(date_col)
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.plot(tmp[date_col], tmp[num_col], color="#E45756")
    ax.set_title(f"{num_col} over {date_col}")
    ax.set_xlabel(date_col)
    ax.set_ylabel(num_col)
    fig.autofmt_xdate()
    return _fig_to_base64(fig)


def generate_charts(df: pd.DataFrame, profiles: List[Dict]) -> List[Dict]:
    """Return a list of {title, image (base64)} chart descriptors."""
    grouped = profiler.columns_by_type(profiles)
    numeric_cols = grouped.get(profiler.NUMERIC, [])
    categorical_cols = grouped.get(profiler.CATEGORICAL, [])
    datetime_cols = grouped.get(profiler.DATETIME, [])

    charts: List[Dict] = []

    for col in numeric_cols[:MAX_NUMERIC]:
        if df[col].notna().any():
            charts.append({"title": f"Numeric: {col}",
                           "image": _numeric_chart(df[col], col)})

    for col in categorical_cols[:MAX_CATEGORICAL]:
        if df[col].notna().any():
            charts.append({"title": f"Categorical: {col}",
                           "image": _categorical_chart(df[col], col)})

    if len(numeric_cols) >= 2:
        charts.append({"title": "Correlation heatmap",
                       "image": _correlation_heatmap(df, numeric_cols[:10])})

    if datetime_cols and numeric_cols:
        charts.append({
            "title": f"Trend: {numeric_cols[0]} over {datetime_cols[0]}",
            "image": _datetime_trend(df, datetime_cols[0], numeric_cols[0]),
        })

    return charts
