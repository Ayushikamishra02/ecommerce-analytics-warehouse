"""Command line: `olist <command>`.

    olist build          download + load raw data, then dbt build (models + 68 tests)
    olist report         figures, CSVs and reports/metrics.json
    olist powerbi        export the star schema to powerbi/data/*.parquet
    olist sql [NN]       run the SQL interview questions (all -> lesson file; NN -> print one)
    olist dashboard      start the Streamlit app
    olist all            build + report + powerbi + sql
"""
from __future__ import annotations

import argparse
import subprocess
import sys

from .ingest import ROOT


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="olist", description="Olist e-commerce analytics warehouse")
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="load raw data and run dbt build")
    b.add_argument("--skip-load", action="store_true", help="re-run dbt only (raw tables already loaded)")
    sub.add_parser("report", help="figures + metrics.json")
    sub.add_parser("powerbi", help="export Parquet files for Power BI")
    s = sub.add_parser("sql", help="SQL interview practice")
    s.add_argument("question", nargs="?", help="question number, e.g. 08")
    sub.add_parser("dashboard", help="streamlit run app/streamlit_app.py")
    sub.add_parser("all", help="build + report + powerbi + sql")
    a = p.parse_args(argv)

    if a.cmd in ("build", "all"):
        from .ingest import main as load_main
        from .warehouse import dbt

        if not getattr(a, "skip_load", False):
            print("1/2 loading raw data into DuckDB")
            load_main()
        print("2/2 dbt build (models + tests)")
        if not dbt("build"):
            sys.exit("dbt build failed: see the output above")
    if a.cmd in ("report", "all"):
        from .report import main as report_main

        report_main()
    if a.cmd in ("powerbi", "all"):
        from .powerbi import main as pbi_main

        pbi_main()
    if a.cmd in ("sql", "all"):
        from . import sqlpractice

        if getattr(a, "question", None):
            sys.argv = ["sqlpractice", a.question]
        else:
            sys.argv = ["sqlpractice"]
        sqlpractice.main()
    if a.cmd == "dashboard":
        sys.exit(subprocess.call([sys.executable, "-m", "streamlit", "run", str(ROOT / "app" / "streamlit_app.py")]))


if __name__ == "__main__":
    main()
