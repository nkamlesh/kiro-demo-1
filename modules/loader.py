"""File / sheet loading logic for the Excel Data Analyzer.

Handles .xlsx, .xlsm (via openpyxl) and legacy .xls (via xlrd), multi-sheet
workbooks, and best-effort header-row auto-detection.
"""
from __future__ import annotations

import io
from typing import List

import pandas as pd


SUPPORTED_EXTENSIONS = (".xlsx", ".xls", ".xlsm")


def _engine_for(filename: str) -> str:
    """Return the pandas engine appropriate for the file extension."""
    name = filename.lower()
    if name.endswith(".xls"):
        return "xlrd"          # legacy binary format
    return "openpyxl"          # .xlsx / .xlsm


def list_sheets(file_bytes: bytes, filename: str) -> List[str]:
    """Return the list of sheet names in an uploaded workbook."""
    engine = _engine_for(filename)
    xls = pd.ExcelFile(io.BytesIO(file_bytes), engine=engine)
    return xls.sheet_names


def _detect_header_row(raw: pd.DataFrame, max_scan: int = 10) -> int:
    """Best-effort detection of the header row index.

    Scans the first ``max_scan`` rows and picks the row that looks most like a
    header: mostly non-null, mostly string values, and all values unique.
    Returns the 0-based row index to use as the header.
    """
    best_row = 0
    best_score = -1.0
    scan = min(max_scan, len(raw))
    for i in range(scan):
        row = raw.iloc[i]
        non_null = row.notna().sum()
        if non_null == 0:
            continue
        values = row.dropna().tolist()
        str_like = sum(1 for v in values if isinstance(v, str))
        unique = len(set(map(str, values)))
        # Reward: high fill ratio, string-ness, and uniqueness of labels.
        fill_ratio = non_null / max(len(row), 1)
        str_ratio = str_like / max(len(values), 1)
        unique_ratio = unique / max(len(values), 1)
        score = fill_ratio + str_ratio + unique_ratio
        if score > best_score:
            best_score = score
            best_row = i
    return best_row


def load_dataframe(
    file_bytes: bytes,
    filename: str,
    sheet_name: str,
    auto_detect_header: bool = True,
) -> pd.DataFrame:
    """Load a single sheet into a cleaned DataFrame.

    When ``auto_detect_header`` is True, blank leading rows are skipped and the
    most likely header row is used.
    """
    engine = _engine_for(filename)
    buffer = io.BytesIO(file_bytes)

    if not auto_detect_header:
        df = pd.read_excel(buffer, sheet_name=sheet_name, engine=engine)
        return _post_process(df)

    # Read raw (no header) to detect the header row, then re-read properly.
    raw = pd.read_excel(
        buffer, sheet_name=sheet_name, engine=engine, header=None
    )
    if raw.empty:
        return raw

    header_row = _detect_header_row(raw)
    buffer.seek(0)
    df = pd.read_excel(
        buffer, sheet_name=sheet_name, engine=engine, header=header_row
    )
    return _post_process(df)


def _post_process(df: pd.DataFrame) -> pd.DataFrame:
    """Drop fully-empty rows/columns and normalise column names."""
    df = df.dropna(axis=0, how="all").dropna(axis=1, how="all")
    df.columns = [str(c).strip() for c in df.columns]
    # Attempt to coerce numeric-looking strings (e.g. "1,000") to numbers.
    for col in df.columns:
        if df[col].dtype == object:
            coerced = _try_numeric(df[col])
            if coerced is not None:
                df[col] = coerced
    df = df.reset_index(drop=True)
    return df


def _try_numeric(series: pd.Series):
    """Return a numeric series if >=90% of non-null values convert, else None."""
    cleaned = series.astype(str).str.replace(",", "", regex=False).str.strip()
    converted = pd.to_numeric(cleaned, errors="coerce")
    non_null = series.notna().sum()
    if non_null == 0:
        return None
    success_ratio = converted.notna().sum() / non_null
    if success_ratio >= 0.9:
        return converted
    return None
