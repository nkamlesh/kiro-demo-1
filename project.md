# Project: Excel Data Analyzer & Insight Generator

## 1. Objective

Build a **Streamlit web application** that lets a user upload any Excel file (`.xlsx`, `.xls`, `.xlsm`), automatically:

1. Detects and profiles all columns (data types, categories vs. numeric vs. dates, etc.)
2. Runs a **data quality check** — missing values, duplicates, outliers, inconsistent types
3. Recommends **how to handle missing values** per column (based on data type & distribution)
4. Generates relevant **charts** based on column types (auto-selected chart types)
5. Produces **3 auto-generated insights** in plain English
6. Exports everything as a **downloadable HTML report**

**Confirmed decisions (from requirements clarification):**

| Decision | Choice |
|---|---|
| Tech stack | Python + Streamlit |
| Interaction mode | Upload file via web UI |
| Output format | Downloadable HTML report |

---

## 2. High-Level Architecture

```
                ┌─────────────────────────┐
                │   Streamlit Web UI      │
                │  (file_uploader widget) │
                └────────────┬────────────┘
                             │  .xlsx / .xls / .xlsm
                             ▼
                ┌─────────────────────────┐
                │   File Loader Module    │
                │  (pandas + openpyxl)    │
                │  - handles multi-sheet  │
                │  - detects header row   │
                └────────────┬────────────┘
                             ▼
                ┌─────────────────────────┐
                │  Column Profiler Module │
                │  - dtype detection      │
                │  - numeric/cat/date tag │
                └────────────┬────────────┘
                             ▼
        ┌────────────────────┴─────────────────────┐
        ▼                                           ▼
┌───────────────────┐                     ┌───────────────────────┐
│ Data Quality Module│                     │  Chart Engine Module  │
│ - missing values   │                     │  - auto chart-type    │
│ - duplicates       │                     │    selection per      │
│ - outliers         │                     │    column type        │
│ - fill recommender │                     │  - matplotlib/plotly  │
└─────────┬──────────┘                     └───────────┬───────────┘
          │                                             │
          └───────────────────┬─────────────────────────┘
                               ▼
                  ┌─────────────────────────┐
                  │   Insight Generator      │
                  │  - correlation checks    │
                  │  - top category checks   │
                  │  - trend/skew checks     │
                  │  - produces top 3 lines  │
                  └────────────┬────────────┘
                               ▼
                  ┌─────────────────────────┐
                  │   HTML Report Builder    │
                  │  (Jinja2 template +      │
                  │   embedded chart images) │
                  └────────────┬────────────┘
                               ▼
                  ┌─────────────────────────┐
                  │  Streamlit Download      │
                  │  Button (report.html)    │
                  └─────────────────────────┘
```

---

## 3. Tech Stack & Dependencies

| Library | Purpose |
|---|---|
| `streamlit` | Web UI, file upload, layout, download button |
| `pandas` | Data loading, cleaning, profiling |
| `openpyxl` | Reading `.xlsx`/`.xlsm` files |
| `xlrd` | Reading legacy `.xls` files |
| `matplotlib` / `seaborn` | Chart generation (static, embeds cleanly in HTML) |
| `plotly` (optional) | Interactive charts if you want a richer HTML report |
| `jinja2` | Templating the final HTML report |
| `numpy` | Numeric computations (outliers, stats) |
| `scipy` (optional) | Skewness/outlier detection (z-score, IQR) |

```bash
pip install streamlit pandas openpyxl xlrd matplotlib seaborn jinja2 numpy scipy plotly
```

---

## 4. Functional Requirements

### 4.1 File Handling
- Accept `.xlsx`, `.xls`, `.xlsm` via `st.file_uploader`
- Support multi-sheet workbooks → let user pick a sheet via dropdown
- Auto-detect header row (handle cases where first row isn't the header)

### 4.2 Column Identification
- Classify every column as: `numeric`, `categorical`, `datetime`, `boolean`, `text/free-form`, `identifier` (e.g., IDs)
- Display a **column summary table**: name, dtype, unique count, % missing, sample values

### 4.3 Data Quality Report
| Check | Method |
|---|---|
| Missing values | `df.isnull().sum()` per column + % of total |
| Duplicates | `df.duplicated().sum()` |
| Outliers (numeric) | IQR method or z-score > 3 |
| Inconsistent types | Mixed types within an "object" column |
| Constant columns | Columns with only 1 unique value (low information) |

### 4.4 Missing Value Recommendations
| Column Type | Recommended Strategy | When to Use |
|---|---|---|
| Numeric (low skew) | Mean imputation | Data roughly symmetric |
| Numeric (high skew) | Median imputation | Skewed distributions, outliers present |
| Categorical | Mode imputation or "Unknown" category | Low cardinality |
| Datetime | Forward-fill / Interpolate | Time-series-like data |
| High missing % (>50%) | Consider dropping column | Recommend, don't auto-drop |
| Identifier columns | Do not impute — flag row for review | IDs must stay unique/valid |

### 4.5 Chart Generation (auto-selected by column type)
| Column Type | Chart |
|---|---|
| Single numeric | Histogram + boxplot |
| Single categorical | Bar chart (top 10 categories) |
| Numeric vs numeric | Scatter plot + correlation heatmap |
| Categorical vs numeric | Grouped bar chart / boxplot by category |
| Datetime vs numeric | Line/trend chart over time |

### 4.6 Insight Generation (3 insights minimum)
Auto-generate using simple rules, e.g.:
- Strongest correlation pair (if `|correlation| > 0.5`)
- Most imbalanced categorical column (e.g., one category = 80%+ of rows)
- Column with highest missing % or most outliers
- Trend direction if a datetime column exists (increasing/decreasing over time)

### 4.7 HTML Report Export
- Single self-contained `.html` file (charts embedded as base64 images)
- Sections: Overview → Column Profile → Data Quality → Missing Value Recommendations → Charts → Insights
- Downloadable via `st.download_button`

---

## 5. Suggested File Structure

```
excel-insight-app/
├── app.py                     # Streamlit entry point
├── modules/
│   ├── loader.py               # File/sheet loading logic
│   ├── profiler.py             # Column type detection
│   ├── quality.py              # Missing values, duplicates, outliers
│   ├── recommender.py          # Fill-value recommendation logic
│   ├── charts.py                # Chart generation functions
│   ├── insights.py              # Insight generation rules
│   └── report.py                 # HTML report builder (Jinja2)
├── templates/
│   └── report_template.html    # Jinja2 HTML template
├── requirements.txt
└── README.md
```

---

## 6. Implementation Plan (Step-by-Step)

| Step | Purpose | Expected Outcome | Common Mistakes | Validation Check |
|---|---|---|---|---|
| **1. Set up Streamlit skeleton** | Create app shell with file uploader | App runs, shows upload widget | Forgetting `st.set_page_config()` first line | `streamlit run app.py` opens without error |
| **2. Load Excel file** | Parse uploaded file into a DataFrame | DataFrame with correct headers/sheet | Not handling `.xls` (needs `xlrd`, not `openpyxl`) | Print `df.shape` and `df.head()` for a test file |
| **3. Profile columns** | Classify each column's type | Summary table with dtype, missing %, unique count | Treating numeric-looking strings ("1,000") as text | Manually check 2-3 columns against expected type |
| **4. Data quality checks** | Compute missing/duplicates/outliers | Quality report dict/table | Using `.mean()` for skewed data outlier detection | Compare missing % sum vs `df.isnull().sum().sum()` |
| **5. Missing value recommender** | Map column type + quality → recommendation | Table of column → suggested strategy | Recommending imputation for ID/key columns | Spot-check recommendations against column semantics |
| **6. Chart engine** | Auto-generate charts per column type | Set of matplotlib/plotly figures | Plotting all columns blindly (too many charts) | Cap charts (e.g., top 10 numeric/categorical columns) |
| **7. Insight generator** | Derive 3+ plain-English insights | List of insight strings | Insights that just restate stats without context | Insights should read like a sentence, not a stat dump |
| **8. HTML report builder** | Combine everything into one HTML file | Single downloadable `.html` | Forgetting to base64-encode chart images (broken links) | Open HTML file standalone (no server) — charts must render |
| **9. Streamlit integration** | Wire modules into the UI with tabs/sections | Full working app end-to-end | Blocking UI on large files (no caching) | Use `@st.cache_data` on load/profile functions |
| **10. Testing across file types** | Validate with different Excel structures | App works on multi-sheet, messy-header files | Only testing with one "clean" sample file | Test: clean file, multi-sheet file, file with blank rows, file with mixed types |

---

## 7. Data Flow Summary

```
Upload → Load (pandas) → Profile columns → 
   ├──> Data Quality Report ──> Fill Recommendations
   └──> Chart Engine ──> Insight Generator
                              ↓
                     HTML Report Builder → Download
```

---

## 8. Deliverables Checklist

- [ ] Streamlit app with file upload (`.xlsx`, `.xls`, `.xlsm`)
- [ ] Multi-sheet selection support
- [ ] Column profiling table (type, missing %, unique count)
- [ ] Data quality report (missing, duplicates, outliers, constant columns)
- [ ] Missing value recommendation table
- [ ] Auto-generated charts based on column type
- [ ] 3+ auto-generated plain-English insights
- [ ] Downloadable self-contained HTML report
- [ ] Caching for performance on large files
- [ ] Tested on at least 3 different Excel file structures

---

## 9. Assumptions vs. Verified Requirements

| Item | Status |
|---|---|
| Tech stack = Python + Streamlit | ✅ Confirmed by user |
| Upload via web UI | ✅ Confirmed by user |
| Output = HTML report | ✅ Confirmed by user |
| Chart library (matplotlib vs plotly) | ⚠️ Assumption — matplotlib recommended for simplicity/static HTML embedding; plotly optional for interactivity |
| Outlier detection method (IQR vs z-score) | ⚠️ Assumption — IQR chosen as default (more robust to skew); verify against your data |
| Max file size supported | ⚠️ Not specified — recommend testing with files up to ~50MB before optimizing further |

---

## 10. Suggested Next Steps

1. Scaffold the project structure and get `app.py` running with just the file uploader (Step 1–2 above).
2. Build and test the column profiler on a few real Excel files you have.
3. Layer in data quality checks, then the recommender.
4. Add charts, then insights, then the HTML export last — this order lets you test each module independently.
5. Once working, consider optional enhancements below.

### Optional Enhancements
- Add a "download cleaned Excel file" option (with missing values filled per recommendation)
- Add interactive Plotly charts instead of static matplotlib for a richer report
- Add a natural-language summary section using an LLM API for more nuanced insights
- Add PDF export as an alternative to HTML (via `weasyprint` or `pdfkit`)
- Add user-adjustable thresholds (e.g., outlier sensitivity, missing % cutoff)

### Learning Resources
- [Streamlit docs — file_uploader](https://docs.streamlit.io/library/api-reference/widgets/st.file_uploader)
- [Pandas docs — working with missing data](https://pandas.pydata.org/docs/user_guide/missing_data.html)
- [Real Python — Exploratory Data Analysis with pandas](https://realpython.com/pandas-python-explore-dataset/)