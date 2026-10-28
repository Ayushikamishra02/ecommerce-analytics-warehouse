# Putting this project on GitHub

## 1. Run it once on your laptop

```powershell
# Windows PowerShell (macOS/Linux: python3 -m venv .venv && source .venv/bin/activate)
cd ecommerce-analytics-warehouse
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[app,dev]"
olist build          # ~1-2 min: downloads 9 CSVs (~120 MB), loads DuckDB, runs dbt build
pytest               # 53 tests should pass
olist report         # regenerates reports/ (already included, so optional)
olist dashboard      # opens the Streamlit app; Ctrl+C to stop
```

If `olist` isn't found, the venv isn't active (your prompt should start with `(.venv)`).
If `olist build` can't download, check that `raw.githubusercontent.com` is reachable on your network.

## 2. Create the repository

1. github.com → **New repository** → name `ecommerce-analytics-warehouse` → Public → **no** README/.gitignore/license
   (the project has them) → Create.
2. In the project folder:

```bash
git init
git add .
git status                      # check: no data/raw/*.csv, no olist.duckdb, no powerbi/data, no .venv
git commit -m "E-commerce analytics warehouse: DuckDB + dbt star schema, tests, analysis, dashboards"
git branch -M main
git remote add origin https://github.com/Ayushikamishra02/ecommerce-analytics-warehouse.git
git push -u origin main
```

3. The CI badge in `README.md` already points at `github.com/Ayushikamishra02/...`; if you use a different
   username or repo name, update that URL.

## 3. Check CI

The **Actions** tab runs `.github/workflows/ci.yml` on every push: install → `olist build` (download, load, dbt
models + 68 data tests) → `pytest` → `ruff`. A green badge on the README shows reviewers that the warehouse builds
from scratch and the tests pass. If the first run fails on the download step, re-run it (temporary network issue).

## 4. Make the repo page look good

- **About** (gear icon on the repo page): description
  *"Star-schema analytics warehouse (DuckDB + dbt, 68 tests) for 100k Brazilian e-commerce orders: KPIs, cohorts,
  RFM, statistics, Streamlit + Power BI"*; topics: `dbt` `duckdb` `data-warehouse` `analytics-engineering`
  `star-schema` `sql` `power-bi` `streamlit` `ecommerce` `data-analysis`.
- **Pin** it on your profile (Customize your pins).
- Add the Power BI screenshots when you've built the dashboard: save them as `docs/powerbi/page1.png` etc. and add
  a "Power BI" section with them to the README.

## 5. Optional extras

- **Host the dbt docs** on GitHub Pages: `./dbt.sh docs generate --static`, copy
  `warehouse/target/static_index.html` to `docs/dbt/index.html`, enable Pages for the `/docs` folder. Reviewers can
  then click through the lineage and column docs.
- **Streamlit Community Cloud** can host the dashboard for free, but it needs the database at startup: you'd add a
  step that runs `olist build` when the app starts if the file is missing (about a minute on first load).

## 6. On your CV / LinkedIn

> **E-commerce Analytics Warehouse** (Python, SQL, dbt, DuckDB, Power BI, Streamlit)
> - Modelled 9 raw tables (100k orders, 1M geolocation rows) into a star schema with dbt: 25 models, 68 data tests
>   including reconciliations; documented and handled 11 data-quality issues.
> - Showed late delivery is the main driver of bad reviews (63% vs 9.5%; odds ratio 18 after controls, bootstrap
>   CI), and that regional rating gaps are explained by lateness.
> - Built KPI, cohort-retention, RFM and seller-Pareto marts; delivered a Streamlit dashboard and a Power BI model
>   with 22 DAX measures.
