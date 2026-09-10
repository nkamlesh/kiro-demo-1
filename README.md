# 📊 Excel Data Analyzer & Insight Generator

A **Streamlit web application** that lets you upload any Excel file (`.xlsx`, `.xls`, `.xlsm`) and automatically:

1. **Profiles all columns** — detects numeric, categorical, datetime, boolean, text, and identifier types
2. Runs a **data-quality check** — missing values, duplicates, outliers (IQR), constant & mixed-type columns
3. Recommends **how to handle missing values** per column (based on type & distribution)
4. Generates **charts** auto-selected by column type (histograms, boxplots, bar charts, correlation heatmap, time trends)
5. Produces **3+ auto-generated insights** in plain English
6. Exports everything as a **downloadable, self-contained HTML report** (charts embedded as base64 — no server needed to view it)

---

## 🗂️ Project Structure

```
excel-insight-app/
├── app.py                     # Streamlit entry point (UI + wiring)
├── modules/
│   ├── __init__.py
│   ├── loader.py              # File/sheet loading + header auto-detection
│   ├── profiler.py            # Column type classification & profiling
│   ├── quality.py             # Missing values, duplicates, outliers, constants
│   ├── recommender.py         # Missing-value strategy recommendations
│   ├── charts.py              # Auto chart generation (matplotlib/seaborn)
│   ├── insights.py            # Rule-based plain-English insights
│   └── report.py              # HTML report builder (Jinja2)
├── templates/
│   └── report_template.html   # Jinja2 HTML report template
├── requirements.txt
└── README.md
```

---

## 🚀 How to Run — Step by Step

> **Prerequisite:** Python **3.10 or newer** installed. Check with `python --version` (or `python3 --version`).

### Step 1 — Get the code

```bash
git clone https://github.com/nkamlesh/kiro-demo-1.git
cd kiro-demo-1
```

### Step 2 — Create a virtual environment

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

Once activated, your prompt shows `(.venv)`.

### Step 3 — Install the dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs Streamlit, pandas, numpy, openpyxl, xlrd, matplotlib, seaborn, scipy, and Jinja2.

### Step 4 — Launch the app

```bash
streamlit run app.py
```

Streamlit prints a local URL (usually **http://localhost:8501**) and opens it in your browser automatically.

### Step 5 — Use the app

1. Click **Browse files** and upload an Excel file (`.xlsx`, `.xls`, or `.xlsm`).
2. If the workbook has multiple sheets, pick one from the **Select a sheet** dropdown.
3. Leave **Auto-detect header row** checked to handle files where the header isn't the first row (uncheck it if the first row is definitely the header).
4. Explore the tabs: **Overview → Column Profile → Data Quality → Recommendations → Charts → Insights**.
5. Click **⬇️ Download HTML report** to save a single, shareable HTML file.

### Step 6 — Stop the app / leave the environment

- Stop Streamlit: press `Ctrl + C` in the terminal.
- Deactivate the virtual environment: `deactivate`

---

## 📄 What's in the HTML Report

The exported report is a single `.html` file containing:

1. **Overview** — row/column counts, total missing cells, duplicate rows
2. **Column Profile** — type, dtype, unique count, missing %, sample values
3. **Data Quality** — duplicates, constant columns, high-missing columns, mixed-type columns, outlier counts
4. **Missing Value Recommendations** — suggested strategy + reasoning per column
5. **Charts** — embedded as base64 images (renders offline, no server required)
6. **Auto-Generated Insights** — plain-English findings

---

## 🧠 How It Decides Things

**Column types** are inferred from dtype, value patterns, cardinality, and column-name hints (e.g. `id`, `code`, `key` → identifier).

**Missing-value recommendations:**

| Column type | Recommended strategy |
|---|---|
| Numeric (low skew, \|skew\| ≤ 1) | Mean imputation |
| Numeric (high skew, \|skew\| > 1) | Median imputation |
| Categorical / Boolean | Mode or an explicit "Unknown" category |
| Datetime | Forward-fill / interpolate |
| Identifier | Do **not** impute — flag rows for review |
| Any column >50% missing | Consider dropping the column |

**Outliers** are detected with the **IQR method** (values below `Q1 − 1.5·IQR` or above `Q3 + 1.5·IQR`).

---

## 🛠️ Troubleshooting

| Issue | Fix |
|---|---|
| `command not found: streamlit` | Make sure the virtual environment is activated (`source .venv/bin/activate`) and `pip install -r requirements.txt` succeeded. |
| `.xls` file won't open | Legacy `.xls` needs **xlrd** (already in `requirements.txt`). Re-run the install. |
| Charts missing in the browser | Large files are cached; try re-uploading. Charts are capped (top 8 numeric / 8 categorical columns) to stay responsive. |
| Port 8501 already in use | Run on another port: `streamlit run app.py --server.port 8502`. |
| App feels slow on big files | Loading and analysis are cached with `@st.cache_data`; the first run is the slowest. |

---

## ⚙️ Tech Stack

Python · Streamlit · pandas · numpy · openpyxl · xlrd · matplotlib · seaborn · scipy · Jinja2
