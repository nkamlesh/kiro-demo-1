# Project Structure

```
kiro-demo-1/
├── app.py                     # Streamlit entry point — UI, tabs, and module wiring
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
├── project.md                 # Original design/requirements spec
└── README.md
```

## Architecture: a linear analysis pipeline

`app.py` orchestrates; the `modules/` package holds all logic. Data flows one way:

```
upload → loader → profiler → { quality → recommender, charts, insights } → report
```

- **`app.py`** — the only Streamlit-aware file for orchestration. Owns the UI (uploader, sheet select, tabs), calls modules, and holds the `@st.cache_data`-wrapped `_list_sheets`, `_load_df`, and `_analyze` wrappers. `st.set_page_config(...)` must be the first Streamlit call.
- **`modules/*`** — pure, framework-agnostic functions that take/return plain data (DataFrames, dicts, lists). Keep Streamlit imports out of `modules/` so the logic stays testable and reusable.
- **`report.py` + `templates/`** — the only place HTML is produced. Charts arrive as base64 strings and are embedded directly.

## Conventions

- Every module starts with a docstring and `from __future__ import annotations`.
- Public functions are fully type-hinted and have docstrings.
- Private helpers are prefixed with an underscore (e.g. `_engine_for`, `_detect_header_row`, `_post_process`).
- Column semantic types are defined as constants in `profiler.py` (`NUMERIC`, `CATEGORICAL`, `DATETIME`, `BOOLEAN`, `TEXT`, `IDENTIFIER`) — reuse them rather than hardcoding strings elsewhere.
- Profiles are passed between modules as `List[Dict]`; quality results as a `Dict`. Preserve these shapes when extending the pipeline.
- Guard user-facing failures in `app.py` with try/except and `st.error(...)` / `st.stop()`; keep module functions free of UI concerns.

## Where things go

- New analysis logic → a function in the relevant `modules/` file (or a new module), wired into `_analyze` in `app.py`.
- New report sections → extend `report.py`'s render context and `templates/report_template.html`.
- New dependencies → add to `requirements.txt` with a pinned lower bound (`>=`).
