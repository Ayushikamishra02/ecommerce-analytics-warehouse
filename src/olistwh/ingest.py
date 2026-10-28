"""Extract + load: download the Olist CSVs (checksums verified) and load them, untouched, into DuckDB's `raw` schema.

Olist is a Brazilian marketplace that connects small shops to big e-commerce sites. Its public dataset has
~100k orders (Sept 2016 - Oct 2018) across 9 linked tables. All cleaning happens later, in dbt (warehouse/).
This file only copies data in faithfully: the "EL" of ELT.
"""
from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
DB = ROOT / "warehouse" / "olist.duckdb"
BASE = "https://raw.githubusercontent.com/dujiaying/olist/master/data/"

FILES = {   # raw table name: (file name, sha256)
    "customers": ("olist_customers_dataset.csv", "983a422239e1712ded753b3bf9ecf47dc73f144d306029dcfa99e70a226883d2"),
    "geolocation": ("olist_geolocation_dataset.csv", "b514f6fc991b9566aeba02aa5d67e2c3630f034b60a0e05aa0d082a3b66d88d6"),
    "order_items": ("olist_order_items_dataset.csv", "0bc4d068c4fe38cbb01bd90e8746e3c613fe7b4baef75fab7b0e329701c3e279"),
    "order_payments": ("olist_order_payments_dataset.csv", "4f713964f2815dbbaa40b9488268c55aac3627bfce5aa96cf58d1f3616de3cc0"),
    "order_reviews": ("olist_order_reviews_dataset.csv", "0dff69f6fed33a13648020198ea94d7ae12afbdd4904186c6cd904e27a3e1ccd"),
    "orders": ("olist_orders_dataset.csv", "8df58ef3d2d7e9944010f7beecd9b75367f5588ec6e3c91cec19ae3345ef9ecf"),
    "products": ("olist_products_dataset.csv", "3e6569628a17fbc75fd206ee357b59e20364b9afa90f5b6cd5b4d624c58aa9cc"),
    "sellers": ("olist_sellers_dataset.csv", "1f643d2b950373b85735e7794b20986f528d7a000432e7c6f9bcbb44d0846a0e"),
    "category_translation": ("product_category_name_translation.csv",
                             "a81f0d1f27b27e7293f761bc79e3ce8f348ee39c4b3ed3e49bde38f478586278"),
}

# Zip-code prefixes look like numbers but are identifiers with leading zeros ("01037"), so they are read as text.
TEXT_COLUMNS = {"customer_zip_code_prefix", "seller_zip_code_prefix", "geolocation_zip_code_prefix"}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(force: bool = False) -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    for fname, sha in FILES.values():
        path = RAW / fname
        if path.exists() and not force and _sha256(path) == sha:
            continue
        print(f"  downloading {fname}")
        urllib.request.urlretrieve(BASE + fname, path)
        if _sha256(path) != sha:
            path.unlink(missing_ok=True)
            raise RuntimeError(f"checksum mismatch for {fname}")


def load(db_path: Path = DB) -> dict:
    """Create/replace raw.<table> for every file. Returns row counts."""
    import duckdb

    download()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path))
    con.execute("create schema if not exists raw")
    counts = {}
    for name, (fname, _) in FILES.items():
        path = (RAW / fname).as_posix()
        cols = con.execute(f"select * from read_csv('{path}', header=true, sample_size=-1) limit 0").description
        types = {c[0]: "VARCHAR" for c in cols if c[0] in TEXT_COLUMNS}
        type_arg = f", types={types}" if types else ""
        con.execute(f"create or replace table raw.{name} as "
                    f"select * from read_csv('{path}', header=true, sample_size=-1{type_arg})")
        counts[name] = con.execute(f"select count(*) from raw.{name}").fetchone()[0]
    con.close()
    return counts


def main() -> None:
    for k, v in load().items():
        print(f"  raw.{k:<22} {v:>10,} rows")


if __name__ == "__main__":
    main()
