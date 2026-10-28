"""Figures for the README and lessons."""
from __future__ import annotations

import matplotlib
import matplotlib.dates

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.ticker import FuncFormatter, PercentFormatter  # noqa: E402

BLUE, ORANGE, PURPLE, GREY, RED, GREEN, TEAL = "#4C72B0", "#DD8452", "#8172B3", "#8C8C8C", "#C44E52", "#55A868", "#64B5CD"
REGION_COLORS = {"Southeast": BLUE, "South": GREEN, "Center-West": PURPLE, "Northeast": ORANGE, "North": RED}

plt.rcParams.update({
    "figure.dpi": 110, "savefig.dpi": 140, "savefig.bbox": "tight", "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.alpha": 0.25, "font.size": 10,
    "axes.titlesize": 11, "axes.titleweight": "bold", "legend.frameon": False,
})
brl_m = FuncFormatter(lambda v, _: f"R${v / 1e6:.1f}M")


def monthly_trend(m: pd.DataFrame):
    m = m.copy()
    m["month"] = pd.to_datetime(m["month"])
    fig, ax = plt.subplots(figsize=(11, 4))
    colors = [BLUE if c else "#C9D3E6" for c in m["is_complete_month"]]
    ax.bar(m["month"], m["gmv"], width=20, color=colors)
    ax.yaxis.set_major_formatter(brl_m)
    ax.set(ylabel="GMV (items + freight, valid sales)", title="Monthly GMV grew 2.4x year on year (light bars: incomplete months)")
    ax2 = ax.twinx()
    c = m[m["is_complete_month"]]
    ax2.plot(c["month"], c["avg_order_value"], "-o", color=ORANGE, ms=3, label="average order value (complete months)")
    ax2.set_ylabel("average order value (R$)", color=ORANGE)
    ax2.set_ylim(0, m["avg_order_value"].max() * 1.6)
    ax2.grid(False)
    bf = m.loc[m["month"] == "2017-11-01"]
    if len(bf):
        ax.annotate("Black Friday\nNov 2017", (bf["month"].iloc[0], bf["gmv"].iloc[0]), xytext=(-95, -10),
                    textcoords="offset points", fontsize=9, arrowprops={"arrowstyle": "->"})
    ax2.legend(loc="upper left")
    return fig


def late_vs_review(buckets: pd.DataFrame, monthly: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(13, 4))
    ax = axes[0]
    cols = [GREEN if "early" in s else RED for s in buckets["lateness"]]
    bars = ax.bar(buckets["lateness"], buckets["bad_review_rate"], color=cols)
    for b, v, n in zip(bars, buckets["bad_review_rate"], buckets["orders"]):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.01, f"{v:.0%}\nn={n:,}", ha="center", fontsize=8)
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.set(ylabel="orders with a 1-2 star review", ylim=(0, 1), title="One late delivery turns most reviews bad")
    ax.tick_params(axis="x", rotation=30)
    ax = axes[1]
    m = monthly[monthly["is_complete_month"]].copy()
    m["month"] = pd.to_datetime(m["month"])
    ax.plot(m["month"], m["late_rate"], "-o", ms=3, color=RED, label="late deliveries")
    ax.plot(m["month"], m["bad_review_rate"], "-o", ms=3, color=PURPLE, label="1-2 star reviews")
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator(bymonth=[1, 4, 7, 10]))
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b %y"))
    ax.set(title="Month by month, late deliveries and bad reviews move together")
    ax.legend()
    fig.tight_layout()
    return fig


def odds_ratios(model: pd.DataFrame):
    keep = {"late": "Delivered late", "multi_seller": "Order from 2+ sellers", "multi_item": "2+ items in order",
            "log_value": "Order value (x2.7)", "C(payment, Treatment('credit_card'))[T.voucher]": "Paid with voucher",
            "C(region, Treatment('Southeast'))[T.Northeast]": "Customer in Northeast",
            "C(region, Treatment('Southeast'))[T.South]": "Customer in South"}
    t = model.loc[[k for k in keep if k in model.index]].copy()
    t.index = [keep[k] for k in t.index]
    t = t.iloc[::-1]
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    y = np.arange(len(t))
    ax.errorbar(t["odds_ratio"], y, xerr=[t["odds_ratio"] - t["ci_low"], t["ci_high"] - t["odds_ratio"]], fmt="o",
                color=PURPLE, capsize=3)
    ax.axvline(1, color="k", lw=1)
    ax.set_xscale("log")
    ax.set_xticks([0.5, 1, 2, 5, 10, 20])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.xaxis.set_minor_formatter(FuncFormatter(lambda v, _: ""))
    ax.set_yticks(y, t.index)
    for yy, v in zip(y, t["odds_ratio"]):
        ax.text(v * 1.12, yy + 0.15, f"{v:.2f}", fontsize=8)
    ax.set(xlabel="odds ratio for a 1-2 star review (log scale, 95% CI)",
           title="Holding other factors equal, lateness dominates")
    return fig


def cohort_heatmap(c: pd.DataFrame, max_months: int = 12):
    c = c[(c["months_since"] >= 1) & (c["months_since"] <= max_months)].copy()
    c["cohort"] = pd.to_datetime(c["cohort_month"]).dt.strftime("%Y-%m")
    piv = c.pivot(index="cohort", columns="months_since", values="retention_rate")
    piv = piv.loc[(piv.index >= "2017-01") & (piv.index <= "2018-06")]
    fig, ax = plt.subplots(figsize=(10, 5.2))
    im = ax.imshow(piv.values * 100, cmap="Blues", aspect="auto", vmin=0, vmax=1.0)
    ax.set_xticks(range(piv.shape[1]), piv.columns)
    ax.set_yticks(range(piv.shape[0]), piv.index)
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            v = piv.values[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v * 100:.1f}", ha="center", va="center", fontsize=7,
                        color="white" if v * 100 > 0.6 else "black")
    ax.grid(False)
    ax.set(xlabel="months after first order", ylabel="first-order month (cohort)",
           title="Share of each cohort ordering again (%): under 1% in any later month")
    fig.colorbar(im, ax=ax, label="% of cohort", shrink=0.8)
    return fig


def rfm(s: pd.DataFrame):
    s = s.sort_values("revenue_share")
    fig, ax = plt.subplots(figsize=(8, 3.8))
    y = np.arange(len(s))
    ax.barh(y + 0.2, s["customer_share"], height=0.38, color=GREY, label="share of customers")
    ax.barh(y - 0.2, s["revenue_share"], height=0.38, color=BLUE, label="share of revenue")
    ax.set_yticks(y, s["segment"])
    ax.xaxis.set_major_formatter(PercentFormatter(1))
    ax.set(title="RFM segments: who brings the revenue")
    ax.legend(loc="lower right")
    return fig


def pareto(s: pd.DataFrame):
    s = s.sort_values("gmv_rank")
    x = s["gmv_rank"] / len(s)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(x, s["cumulative_gmv_share"], color=BLUE, lw=2)
    ax.plot([0, 1], [0, 1], color=GREY, ls="--", lw=1, label="all sellers equal")
    k = s.loc[s["cumulative_gmv_share"] >= 0.8, "gmv_rank"].min()
    ax.axhline(0.8, color=RED, lw=1, ls=":")
    ax.axvline(k / len(s), color=RED, lw=1, ls=":")
    ax.text(k / len(s) + 0.02, 0.5, f"{k / len(s):.0%} of sellers\n= 80% of GMV", color=RED, fontsize=9)
    ax.xaxis.set_major_formatter(PercentFormatter(1))
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.set(xlabel="sellers, largest first", ylabel="cumulative share of GMV", title="Seller concentration")
    ax.legend(loc="lower right")
    return fig


def states(st: pd.DataFrame):
    st = st.sort_values("avg_delivery_days")
    fig, ax = plt.subplots(figsize=(11, 3.8))
    ax.bar(st["state"], st["avg_delivery_days"], color=[REGION_COLORS[r] for r in st["region"]])
    ax.set(ylabel="average delivery time (days)", title="Delivery time by customer state, coloured by region")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in REGION_COLORS.values()]
    ax.legend(handles, REGION_COLORS.keys(), ncol=5, loc="upper left")
    return fig


def brazil_map(pts: pd.DataFrame, sellers: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(7, 7))
    sc = ax.scatter(pts["lng"], pts["lat"], c=pts["avg_delivery_days"].clip(upper=30), s=2, cmap="RdYlGn_r",
                    alpha=0.7, linewidths=0)
    ax.scatter(sellers["lng"], sellers["lat"], s=2, color="k", alpha=0.25, label="sellers")
    ax.set_aspect("equal")
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    fig.colorbar(sc, ax=ax, shrink=0.6, label="average delivery days (customers in this zip area)")
    ax.legend(loc="lower left", markerscale=4)
    ax.set_title("Sellers are concentrated in the Southeast; far-away customers wait longest")
    return fig


def lifecycle(f: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 3.4))
    y = np.arange(len(f))[::-1]
    ax.barh(y, f["orders"], color=[BLUE, BLUE, BLUE, GREEN, PURPLE])
    for yy, (_, r) in zip(y, f.iterrows()):
        lab = f"{r['orders']:,}"
        if pd.notna(r["median_hours_from_previous"]):
            h = r["median_hours_from_previous"]
            lab += f"   (median {h:.1f} h after previous step)" if h < 48 else f"   (median {h / 24:.1f} days after previous step)"
        ax.text(r["orders"] * 0.02, yy, lab, va="center", color="white", fontsize=9, fontweight="bold")
    ax.set_yticks(y, f["stage"])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.set(xlabel="orders", title="Order lifecycle: where the time goes")
    return fig
