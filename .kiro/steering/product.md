# Product

**Excel Data Analyzer & Insight Generator** — a Streamlit web app for automated exploratory data analysis of Excel files.

## What it does

A user uploads an Excel file (`.xlsx`, `.xls`, `.xlsm`) and the app automatically:

1. **Profiles columns** — classifies each column as numeric, categorical, datetime, boolean, text, or identifier, with dtype, unique count, missing %, and sample values.
2. **Runs data-quality checks** — missing values, duplicate rows, outliers (IQR method), constant columns, and mixed-type columns.
3. **Recommends missing-value strategies** per column based on type and distribution (e.g. mean vs. median imputation, mode, forward-fill, or flag-for-review).
4. **Generates charts** auto-selected by column type (histograms, boxplots, bar charts, correlation heatmaps, time trends).
5. **Produces plain-English insights** using rule-based heuristics (correlations, category imbalance, missingness, trends).
6. **Exports a self-contained HTML report** with charts embedded as base64 — renders offline, no server required.

## Key principles

- **Zero-config analysis** — the app infers structure (header row, column types, numeric-looking strings) without user setup.
- **Recommend, don't mutate** — the app suggests fixes (e.g. dropping high-missing columns) but never auto-modifies the user's data.
- **Responsive on large files** — heavy operations are cached; charts are capped to stay fast.
- **Portable output** — the HTML report is a single shareable file that works without a server.
