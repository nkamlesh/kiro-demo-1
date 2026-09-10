# Tech Stack

## Language & Runtime

- **Python 3.10+** (uses `from __future__ import annotations` and modern typing).

## Core Libraries

| Library | Purpose |
|---|---|
| `streamlit` (>=1.32) | Web UI, file upload, layout, caching, download button |
| `pandas` (>=2.0) | Data loading, cleaning, profiling |
| `numpy` (>=1.24) | Numeric computation / stats |
| `openpyxl` (>=3.1) | Read `.xlsx` / `.xlsm` |
| `xlrd` (>=2.0) | Read legacy `.xls` |
| `matplotlib` (>=3.7) | Static charts (embed cleanly as base64 in HTML) |
| `seaborn` (>=0.12) | Statistical charts |
| `scipy` (>=1.10) | Skewness / outlier statistics |
| `jinja2` (>=3.1) | HTML report templating |

Charts are intentionally **static (matplotlib/seaborn)** so they can be base64-embedded into a self-contained HTML report. Do not introduce interactive chart libraries (e.g. Plotly) into the report path without reason.

## Common Commands

Setup (Windows PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

Run on an alternate port (if 8501 is taken):

```bash
streamlit run app.py --server.port 8502
```

There is currently no test suite, linter config, or build step in the repo. If adding tooling, prefer `pytest` for tests.

## Performance conventions

- Wrap expensive load/profile/analyze functions with `@st.cache_data`.
- Cache keys are the raw file bytes + parameters (not the `UploadedFile` object).
- Cap the number of charts generated (top numeric / categorical columns) to keep the UI responsive.
