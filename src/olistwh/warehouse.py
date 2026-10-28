"""Build and connect to the warehouse.

    python -m olistwh.warehouse      # load raw data + `dbt build` (models AND tests)
"""
from __future__ import annotations

import os
from pathlib import Path

from .ingest import DB, ROOT, load

DBT_DIR = ROOT / "warehouse"


def dbt(*args: str) -> bool:
    """Run a dbt command programmatically (same as `dbt <args>` in the warehouse/ folder)."""
    from dbt.cli.main import dbtRunner

    os.environ.setdefault("OLIST_DB", str(DB))
    res = dbtRunner().invoke([*args, "--project-dir", str(DBT_DIR), "--profiles-dir", str(DBT_DIR)])
    return bool(res.success)


def build(load_raw: bool = True) -> bool:
    if load_raw:
        load()
    return dbt("build")


def connect(read_only: bool = True):
    import duckdb

    if not Path(DB).exists():
        raise FileNotFoundError(f"{DB} not found: run `olist build` first")
    return duckdb.connect(str(DB), read_only=read_only)


def main() -> None:
    ok = build()
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
