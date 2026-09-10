"""Excel Data Analyzer & Insight Generator — Streamlit entry point.

Upload an Excel file (.xlsx / .xls / .xlsm) and get automated column profiling,
data-quality checks, missing-value recommendations, charts, plain-English
insights, and a downloadable self-contained HTML report.

Run with:  streamlit run app.py
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from modules import charts, insights, loader, profiler, quality, recommender, report

st.set_page_config(  # must be the first Streamlit call
    page_title="Excel Data Analyzer & Insight Generator",
    page_icon="📊",
    layout="wide",
)


# ---------- Cached heavy operations ----------
@st.cache_data(show_spinner=False)
def _list_sheets(file_bytes: bytes, filename: str):
    return loader.list_sheets(file_bytes, filename)


@st.cache_data(show_spinner=False)
def _load_df(file_bytes: bytes, filename: str, sheet: str, auto_header: bool):
    return loader.load_dataframe(file_bytes, filename, sheet, auto_header)


@st.cache_data(show_spinner=False)
def _analyze(df: pd.DataFrame):
    profiles = profiler.profile_columns(df)
    q = quality.run_quality_checks(df, profiles)
    recs = recommender.recommend(df, profiles, q)
    figs = charts.generate_charts(df, profiles)
    ins = insights.generate_insights(df, profiles, q)
    return profiles, q, recs, figs, ins


# ---------- UI ----------
st.title("📊 Excel Data Analyzer & Insight Generator")
st.caption(
    "Upload an Excel file to automatically profile columns, check data quality, "
    "get missing-value recommendations, view charts, and download an HTML report."
)

uploaded = st.file_uploader(
    "Upload an Excel file",
    type=["xlsx", "xls", "xlsm"],
    help="Supported formats: .xlsx, .xls, .xlsm",
)

if uploaded is None:
    st.info("👆 Upload a file to begin.")
    st.stop()

file_bytes = uploaded.getvalue()
filename = uploaded.name

# Sheet selection (multi-sheet support).
try:
    sheets = _list_sheets(file_bytes, filename)
except Exception as exc:  # noqa: BLE001
    st.error(f"Could not read the workbook: {exc}")
    st.stop()

col_a, col_b = st.columns([2, 1])
with col_a:
    sheet = st.selectbox("Select a sheet", sheets)
with col_b:
    auto_header = st.checkbox("Auto-detect header row", value=True)

try:
    df = _load_df(file_bytes, filename, sheet, auto_header)
except Exception as exc:  # noqa: BLE001
    st.error(f"Failed to load sheet '{sheet}': {exc}")
    st.stop()

if df.empty:
    st.warning("The selected sheet is empty after removing blank rows/columns.")
    st.stop()

profiles, q, recs, figs, ins = _analyze(df)

# Tabs for each section.
tab_overview, tab_profile, tab_quality, tab_reco, tab_charts, tab_insights = st.tabs(
    ["Overview", "Column Profile", "Data Quality", "Recommendations", "Charts", "Insights"]
)

with tab_overview:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", q["n_rows"])
    c2.metric("Columns", q["n_cols"])
    c3.metric("Missing cells", q["total_missing_cells"])
    c4.metric("Duplicate rows", q["duplicate_rows"])
    st.subheader("Data preview")
    st.dataframe(df.head(20), use_container_width=True)

with tab_profile:
    st.subheader("Column profile")
    st.dataframe(pd.DataFrame(profiles), use_container_width=True)

with tab_quality:
    st.subheader("Data quality checks")
    st.write(f"**Duplicate rows:** {q['duplicate_rows']}")
    st.write(
        "**Constant columns:** "
        + (", ".join(q["constant_columns"]) if q["constant_columns"] else "None")
    )
    st.write(
        "**High-missing (>50%) columns:** "
        + (", ".join(q["high_missing_columns"]) if q["high_missing_columns"] else "None")
    )
    st.write(
        "**Mixed-type columns:** "
        + (", ".join(q["mixed_type_columns"]) if q["mixed_type_columns"] else "None")
    )
    if q["outliers"]:
        st.subheader("Outliers (IQR method)")
        st.dataframe(
            pd.DataFrame(
                [{"column": c, "outliers": n} for c, n in q["outliers"].items()]
            ),
            use_container_width=True,
        )

with tab_reco:
    st.subheader("Missing-value recommendations")
    st.dataframe(pd.DataFrame(recs), use_container_width=True)

with tab_charts:
    st.subheader("Auto-generated charts")
    if not figs:
        st.write("No charts could be generated for this dataset.")
    for c in figs:
        st.markdown(f"**{c['title']}**")
        st.image(f"data:image/png;base64,{c['image']}", use_container_width=True)

with tab_insights:
    st.subheader("Auto-generated insights")
    for i in ins:
        st.info(i)

# ---------- HTML report download ----------
st.divider()
html = report.build_html_report(filename, sheet, profiles, q, recs, figs, ins)
st.download_button(
    "⬇️ Download HTML report",
    data=html,
    file_name=f"{filename.rsplit('.', 1)[0]}_report.html",
    mime="text/html",
    type="primary",
)
