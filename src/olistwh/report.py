"""Rebuild every figure, table and number used in the README and lessons (needs a built warehouse).

    python -m olistwh.report
"""
from __future__ import annotations

import json
import shutil
import subprocess

import pandas as pd

from . import viz
from .analysis import Q, all_findings, data_quality, late_review_model, regions, rfm_summary
from .ingest import ROOT
from .warehouse import DBT_DIR, connect

REPORTS = ROOT / "reports"
FIG = REPORTS / "figures"


def _r(df: pd.DataFrame, n: int = 4) -> pd.DataFrame:
    """Round numeric columns only (pandas warns when asked to round dates)."""
    return df.round({c: n for c in df.select_dtypes("number").columns})


def _save(fig, name):
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / name)
    viz.plt.close(fig)


def lineage_graph() -> bool:
    """Draw the dbt model graph from target/manifest.json with Graphviz (skipped if `dot` isn't installed)."""
    manifest = DBT_DIR / "target" / "manifest.json"
    if not manifest.exists() or shutil.which("dot") is None:
        return False
    m = json.loads(manifest.read_text())
    color = {"source": "#E8E8E8", "seed": "#FFF2CC", "staging": "#DAE8FC", "intermediate": "#E1D5E7",
             "core": "#D5E8D4", "analytics": "#F8CECC"}
    lines = ["digraph G {", 'rankdir=LR; node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=10];',
             'edge [color="#999999"];']
    names = {}
    for uid, s in m["sources"].items():
        names[uid] = f"raw.{s['name']}"
        lines.append(f'"{names[uid]}" [fillcolor="{color["source"]}"];')
    for uid, n in m["nodes"].items():
        if n["resource_type"] not in ("model", "seed"):
            continue
        layer = "seed" if n["resource_type"] == "seed" else n["config"].get("schema") or "core"
        names[uid] = n["name"]
        lines.append(f'"{n["name"]}" [fillcolor="{color.get(layer, "#FFFFFF")}"];')
    for uid, n in m["nodes"].items():
        if uid in names:
            for dep in n["depends_on"].get("nodes", []):
                if dep in names:
                    lines.append(f'"{names[dep]}" -> "{names[uid]}";')
    lines.append("}")
    dot = REPORTS / "lineage.dot"
    dot.write_text("\n".join(lines))
    subprocess.run(["dot", "-Tpng", "-Gdpi=130", str(dot), "-o", str(FIG / "10_dbt_lineage.png")], check=True)
    return True


def build() -> dict:
    con = connect()
    REPORTS.mkdir(exist_ok=True)
    M = all_findings(con)

    monthly = Q(con, "select * from analytics.mart_monthly_kpis order by month")
    _r(monthly, 4).to_csv(REPORTS / "monthly_kpis.csv", index=False)
    _save(viz.monthly_trend(monthly), "01_monthly_trend.png")

    buckets = Q(con, "select * from analytics.mart_delivery_vs_review order by sort_key")
    _r(buckets, 4).to_csv(REPORTS / "delivery_vs_review.csv", index=False)
    _save(viz.late_vs_review(buckets, monthly), "02_late_vs_review.png")
    M["delivery_buckets"] = _r(buckets, 4).to_dict("records")

    model = late_review_model(con)
    _r(model, 4).to_csv(REPORTS / "bad_review_logit_odds_ratios.csv")
    _save(viz.odds_ratios(model), "03_odds_ratios.png")
    keep = ["late", "multi_seller", "multi_item", "log_value", "freight_share"]
    M["late_model"]["other_odds_ratios"] = {k: round(float(model.loc[k, "odds_ratio"]), 3) for k in keep}

    cohort = Q(con, "select * from analytics.mart_cohort_retention")
    _save(viz.cohort_heatmap(cohort), "04_cohort_retention.png")

    rfm = rfm_summary(con)
    _r(rfm, 4).to_csv(REPORTS / "rfm_segments.csv", index=False)
    _save(viz.rfm(rfm), "05_rfm_segments.png")
    M["rfm"] = _r(rfm, 4).to_dict("records")

    sellers = Q(con, "select * from analytics.mart_seller_performance")
    _save(viz.pareto(sellers), "06_seller_pareto.png")

    st = Q(con, "select * from analytics.mart_state_delivery")
    _r(st, 4).to_csv(REPORTS / "state_delivery.csv", index=False)
    _save(viz.states(st), "07_delivery_by_state.png")
    reg = regions(con)
    _r(reg, 4).to_csv(REPORTS / "region_delivery.csv", index=False)
    M["regions"] = _r(reg, 4).to_dict("records")

    pts = Q(con, """
        select g.lat, g.lng, avg(o.delivery_days) as avg_delivery_days, count(*) as orders
        from core.fct_orders o
        join core.dim_customers c using (customer_key)
        join staging.stg_geolocation g on g.zip_prefix = c.zip_prefix
        where o.is_delivered group by 1, 2""")
    sl = Q(con, "select lat, lng from core.dim_sellers where lat is not null")
    _save(viz.brazil_map(pts, sl), "08_brazil_map.png")

    life = Q(con, "select * from analytics.mart_order_lifecycle order by step")
    _save(viz.lifecycle(life), "09_order_lifecycle.png")
    M["lifecycle"] = _r(life, 2).to_dict("records")

    dq = data_quality(con)
    dq.to_csv(REPORTS / "data_quality.csv", index=False)
    M["data_quality"] = dq.to_dict("records")
    M["lineage_drawn"] = lineage_graph()

    counts = {t: con.execute(f"select count(*) from {t}").fetchone()[0] for t in
              ["core.fct_orders", "core.fct_order_items", "core.dim_customers", "core.dim_products", "core.dim_sellers",
               "core.dim_date"]}
    M["table_rows"] = counts
    (REPORTS / "metrics.json").write_text(json.dumps(M, indent=2, default=str))
    return M


def main() -> None:
    m = build()
    print(json.dumps({k: m[k] for k in ("growth", "late_vs_review", "late_model")}, indent=1, default=str)[:1500])
    print("-> reports/")


if __name__ == "__main__":
    pd.set_option("display.width", 160)
    main()
