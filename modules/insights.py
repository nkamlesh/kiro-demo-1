"""Rule-based generation of plain-English insights."""
from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd

from . import profiler


def generate_insights(df: pd.DataFrame, profiles: List[Dict], quality: Dict) -> List[str]:
    """Produce a prioritised list of plain-English insights (3+ where possible)."""
    grouped = profiler.columns_by_type(profiles)
    numeric_cols = grouped.get(profiler.NUMERIC, [])
    categorical_cols = grouped.get(profiler.CATEGORICAL, [])
    datetime_cols = grouped.get(profiler.DATETIME, [])

    insights: List[str] = []

    # 1. Strongest correlation pair among numeric columns.
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr(numeric_only=True).abs()
        np.fill_diagonal(corr.values, 0)
        if not corr.isna().all().all():
            max_val = corr.max().max()
            if max_val >= 0.5:
                pair = corr.stack().idxmax()
                signed = df[numeric_cols].corr(numeric_only=True).loc[pair[0], pair[1]]
                direction = "positive" if signed > 0 else "negative"
                insights.append(
                    f"'{pair[0]}' and '{pair[1]}' show a strong {direction} "
                    f"relationship (correlation {signed:.2f}) — as one changes, "
                    f"the other tends to move {'together' if signed > 0 else 'in the opposite direction'}."
                )

    # 2. Most imbalanced categorical column.
    most_imbalanced = None
    max_share = 0.0
    for col in categorical_cols:
        vc = df[col].value_counts(normalize=True, dropna=True)
        if len(vc) > 0 and vc.iloc[0] > max_share:
            max_share = vc.iloc[0]
            most_imbalanced = (col, vc.index[0], vc.iloc[0])
    if most_imbalanced and max_share >= 0.6:
        col, top_cat, share = most_imbalanced
        insights.append(
            f"'{col}' is heavily imbalanced: '{top_cat}' accounts for "
            f"{share * 100:.0f}% of all rows, so this column carries limited "
            f"discriminating information."
        )

    # 3. Column with the highest missing percentage.
    missing_items = [(c, m["pct"]) for c, m in quality["missing"].items() if m["pct"] > 0]
    if missing_items:
        worst_col, worst_pct = max(missing_items, key=lambda x: x[1])
        insights.append(
            f"'{worst_col}' has the most missing data ({worst_pct}%), which should "
            f"be addressed before analysis to avoid biased results."
        )

    # 4. Column with the most outliers.
    if quality["outliers"]:
        col, count = max(quality["outliers"].items(), key=lambda x: x[1])
        if count > 0:
            insights.append(
                f"'{col}' contains {count} statistical outlier(s) (IQR method), "
                f"which may indicate data-entry errors or genuinely extreme values "
                f"worth investigating."
            )

    # 5. Trend direction for a datetime + numeric pair.
    if datetime_cols and numeric_cols:
        tmp = df[[datetime_cols[0], numeric_cols[0]]].dropna().copy()
        tmp[datetime_cols[0]] = pd.to_datetime(tmp[datetime_cols[0]], errors="coerce")
        tmp = tmp.dropna().sort_values(datetime_cols[0])
        if len(tmp) >= 3:
            first_half = tmp[numeric_cols[0]].iloc[: len(tmp) // 2].mean()
            second_half = tmp[numeric_cols[0]].iloc[len(tmp) // 2 :].mean()
            if first_half != 0:
                change = (second_half - first_half) / abs(first_half) * 100
                if abs(change) >= 5:
                    direction = "increasing" if change > 0 else "decreasing"
                    insights.append(
                        f"'{numeric_cols[0]}' shows an overall {direction} trend over "
                        f"'{datetime_cols[0]}' (~{abs(change):.0f}% change between the "
                        f"earlier and later periods)."
                    )

    # 6. Duplicate rows.
    if quality["duplicate_rows"] > 0:
        insights.append(
            f"The dataset contains {quality['duplicate_rows']} duplicate row(s); "
            f"consider de-duplicating to avoid double-counting."
        )

    # Fallbacks to always return at least 3 insights.
    if len(insights) < 3:
        insights.append(
            f"The dataset has {quality['n_rows']} rows and {quality['n_cols']} columns "
            f"with {quality['total_missing_cells']} missing cells in total."
        )
    if len(insights) < 3 and quality["constant_columns"]:
        insights.append(
            f"Constant column(s) detected ({', '.join(quality['constant_columns'])}) — "
            f"these carry no information and can usually be dropped."
        )
    if len(insights) < 3:
        insights.append(
            "No strong statistical patterns were detected; the data appears fairly "
            "uniform across the profiled columns."
        )

    return insights[:6]
