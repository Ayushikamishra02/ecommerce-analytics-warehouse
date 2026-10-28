"""Export the star schema for Power BI (or Tableau / Excel).

    python -m olistwh.powerbi      -> powerbi/data/*.parquet

Power BI Desktop: Get Data -> Parquet (or Folder) -> pick the files in powerbi/data/.
The relationships, DAX measures, theme and page-by-page build guide are in the powerbi/ folder.
"""
from __future__ import annotations

from .ingest import ROOT
from .warehouse import connect

OUT = ROOT / "powerbi" / "data"

# Exported table -> SQL. Column names are kept identical to the warehouse so DAX in measures.dax works.
TABLES = {
    "fct_orders": """select order_id, customer_key, purchase_date, purchase_month, order_status, is_valid_sale,
                            is_delivered, customer_state, customer_region, items_value, freight_value, order_value,
                            payment_total, payment_type, installments, used_voucher, n_items, n_sellers,
                            main_category, avg_distance_km, delivery_days, promised_days, days_late, is_late,
                            review_score, is_bad_review, customer_order_number
                     from core.fct_orders""",
    "fct_order_items": """select order_id, order_item_id, product_id, seller_id, customer_key, purchase_date,
                                 item_price, item_freight, item_value, category, seller_state, distance_km,
                                 is_valid_sale, is_late, review_score
                          from core.fct_order_items""",
    "dim_customers": "select * from core.dim_customers",
    "dim_products": "select * from core.dim_products",
    "dim_sellers": "select * from core.dim_sellers",
    "dim_date": "select * from core.dim_date",
    "mart_cohort_retention": "select * from analytics.mart_cohort_retention",
    "mart_rfm": "select * from analytics.mart_rfm",
    "mart_seller_performance": "select * from analytics.mart_seller_performance",
}


def export(out=OUT) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    con = connect()
    sizes = {}
    for name, sql in TABLES.items():
        path = (out / f"{name}.parquet").as_posix()
        con.execute(f"copy ({sql}) to '{path}' (format parquet, compression zstd)")
        sizes[name] = con.execute(f"select count(*) from read_parquet('{path}')").fetchone()[0]
    con.close()
    return sizes


def main() -> None:
    for k, v in export().items():
        print(f"  powerbi/data/{k}.parquet  {v:>9,} rows")


if __name__ == "__main__":
    main()
