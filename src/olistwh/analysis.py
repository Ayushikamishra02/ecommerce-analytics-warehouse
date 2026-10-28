"""Business questions answered from the warehouse marts, with the statistics behind each answer.

Every function takes an open DuckDB connection to the built warehouse and returns plain Python/pandas objects,
so the same logic feeds the report, the dashboard and the tests.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .warehouse import connect

Q = lambda con, sql: con.execute(sql).df()  # noqa: E731


# --------------------------------------------------------------------------- 1. growth
def growth(con) -> dict:
    m = Q(con, "select * from analytics.mart_monthly_kpis where is_complete_month order by month")
    m["month"] = pd.to_datetime(m["month"])
    jan_aug = lambda y: m[(m.month.dt.year == y) & (m.month.dt.month <= 8)]  # noqa: E731
    g17, g18 = jan_aug(2017), jan_aug(2018)
    daily = Q(con, """select purchase_date, count(*) as orders from core.fct_orders
                      where is_valid_sale and purchase_month = '2017-11-01' group by 1""")
    bf = daily.loc[pd.to_datetime(daily.purchase_date) == "2017-11-24", "orders"].iloc[0]
    rest = daily.loc[pd.to_datetime(daily.purchase_date) != "2017-11-24", "orders"].median()
    best = m.loc[m.gmv.idxmax()]
    return {
        "complete_months": len(m),
        "gmv_total_complete_months": float(m.gmv.sum()),
        "orders_total_complete_months": int(m.orders.sum()),
        "gmv_jan_aug_2017": float(g17.gmv.sum()), "gmv_jan_aug_2018": float(g18.gmv.sum()),
        "gmv_growth_jan_aug": float(g18.gmv.sum() / g17.gmv.sum() - 1),
        "orders_growth_jan_aug": float(g18.orders.sum() / g17.orders.sum() - 1),
        "aov_2017": float(g17.gmv.sum() / g17.orders.sum()), "aov_2018": float(g18.gmv.sum() / g18.orders.sum()),
        "black_friday_2017_orders": int(bf), "november_2017_median_daily_orders": float(rest),
        "best_month": str(best.month.date()), "best_month_gmv": float(best.gmv),
    }


# --------------------------------------------------------------------------- 2. late delivery and reviews
def late_vs_review(con, n_boot: int = 2000, seed: int = 0) -> dict:
    d = Q(con, """select is_late, is_bad_review::int as bad, review_score from core.fct_orders
                  where is_delivered and has_review""")
    late, on_time = d[d.is_late], d[~d.is_late]
    rng = np.random.default_rng(seed)
    a, b = late["bad"].to_numpy(), on_time["bad"].to_numpy()
    boots = np.array([rng.choice(a, len(a)).mean() - rng.choice(b, len(b)).mean() for _ in range(n_boot)])
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {
        "delivered_reviewed_orders": len(d), "late_share": float(d.is_late.mean()),
        "bad_review_rate_late": float(a.mean()), "bad_review_rate_on_time": float(b.mean()),
        "difference": float(a.mean() - b.mean()), "difference_ci": [float(lo), float(hi)],
        "avg_review_late": float(late.review_score.mean()), "avg_review_on_time": float(on_time.review_score.mean()),
        "share_of_bad_reviews_from_late_orders": float(late["bad"].sum() / d["bad"].sum()),
    }


def late_review_model(con) -> pd.DataFrame:
    """Logistic regression: does lateness predict a bad review AFTER accounting for region, order size,
    freight share, payment type and product category? Returns odds ratios with 95% CIs."""
    import statsmodels.formula.api as smf

    d = Q(con, """
        select is_bad_review::int as bad, is_late::int as late, customer_region as region,
               ln(order_value) as log_value, freight_value / nullif(order_value, 0) as freight_share,
               n_items > 1 as multi_item, n_sellers > 1 as multi_seller, payment_type as payment,
               main_category
        from core.fct_orders
        where is_delivered and has_review and order_value > 0 and payment_type is not null""")
    top = d.main_category.value_counts().head(15).index
    d["category"] = np.where(d.main_category.isin(top), d.main_category, "other")
    d["multi_item"] = d.multi_item.astype(int)
    d["multi_seller"] = d.multi_seller.astype(int)
    m = smf.logit("bad ~ late + C(region, Treatment('Southeast')) + log_value + freight_share + multi_item"
                  " + multi_seller + C(payment, Treatment('credit_card')) + C(category, Treatment('other'))",
                  data=d).fit(disp=False)
    ci = m.conf_int()
    out = pd.DataFrame({"odds_ratio": np.exp(m.params), "ci_low": np.exp(ci[0]), "ci_high": np.exp(ci[1]),
                        "p_value": m.pvalues})
    out.attrs["n"] = int(m.nobs)
    return out


def monthly_late_review_correlation(con) -> dict:
    from scipy import stats

    m = Q(con, "select month, late_rate, bad_review_rate from analytics.mart_monthly_kpis where is_complete_month")
    rho, p = stats.spearmanr(m.late_rate, m.bad_review_rate)
    worst = m.sort_values("late_rate", ascending=False).head(2)
    return {"spearman_rho": float(rho), "p_value": float(p), "months": len(m),
            "worst_months": [str(pd.Timestamp(x).date()) for x in worst.month],
            "worst_months_late_rate": [float(x) for x in worst.late_rate],
            "worst_months_bad_review_rate": [float(x) for x in worst.bad_review_rate]}


# --------------------------------------------------------------------------- 3. customers
def retention(con) -> dict:
    r = Q(con, "select * from analytics.mart_rfm")
    second = Q(con, """
        with o as (select customer_key, purchased_at, customer_order_number from core.fct_orders where is_valid_sale)
        select date_diff('day', a.purchased_at, b.purchased_at) as days
        from o a join o b on a.customer_key = b.customer_key
        where a.customer_order_number = 1 and b.customer_order_number = 2""")
    coh = Q(con, """select months_since, sum(active_customers) / sum(cohort_size) as rate
                    from analytics.mart_cohort_retention
                    where cohort_month between '2017-01-01' and '2017-12-01' and months_since between 1 and 6
                    group by 1 order by 1""")
    return {"customers": len(r), "repeat_customers": int((r.frequency >= 2).sum()),
            "repeat_rate": float((r.frequency >= 2).mean()),
            "median_days_to_second_order": float(second.days.median()) if len(second) else None,
            "second_order_same_day_share": float((second.days == 0).mean()) if len(second) else None,
            "retention_month_1_2017_cohorts": float(coh.loc[coh.months_since == 1, "rate"].iloc[0]),
            "retention_months_1_6_2017_cohorts": [float(x) for x in coh.rate]}


def rfm_summary(con) -> pd.DataFrame:
    s = Q(con, """select segment, count(*) as customers, sum(monetary) as revenue, avg(monetary) as avg_spend,
                         avg(recency_days) as avg_recency_days
                  from analytics.mart_rfm group by 1""")
    s["customer_share"] = s.customers / s.customers.sum()
    s["revenue_share"] = s.revenue / s.revenue.sum()
    return s.sort_values("revenue", ascending=False).reset_index(drop=True)


# --------------------------------------------------------------------------- 4. sellers and geography
def sellers(con) -> dict:
    s = Q(con, "select * from analytics.mart_seller_performance order by gmv_rank")
    n80 = int(s.loc[s.cumulative_gmv_share >= 0.8, "gmv_rank"].min())
    big = s[s.orders >= 30]
    bad = big[big.avg_review_score < 3.5]
    return {"sellers": len(s), "sellers_for_80pct_gmv": n80, "share_of_sellers_for_80pct_gmv": n80 / len(s),
            "top_10pct_gmv_share": float(s.head(int(len(s) * 0.1)).gmv.sum() / s.gmv.sum()),
            "sellers_with_30plus_orders": len(big), "of_which_avg_review_below_3_5": len(bad),
            "their_gmv_share": float(bad.gmv.sum() / s.gmv.sum()),
            "late_rate_low_rated_vs_others": [float(bad.late_rate.mean()), float(big.drop(bad.index).late_rate.mean())]}


def regions(con) -> pd.DataFrame:
    return Q(con, """
        select region, sum(delivered_orders) as delivered_orders,
               sum(avg_delivery_days * delivered_orders) / sum(delivered_orders) as avg_delivery_days,
               sum(late_rate * delivered_orders) / sum(delivered_orders) as late_rate,
               sum(freight_share * delivered_orders) / sum(delivered_orders) as freight_share,
               sum(avg_review_score * delivered_orders) / sum(delivered_orders) as avg_review_score
        from analytics.mart_state_delivery group by 1 order by avg_delivery_days""")


def data_quality(con) -> pd.DataFrame:
    """The issues found in the raw data and how the warehouse handles each one."""
    one = lambda sql: con.execute(sql).fetchone()[0]  # noqa: E731
    rows = [
        ("Repeated review_id rows", one("select count(*) - count(distinct review_id) from raw.order_reviews"),
         "stg_reviews keeps one review per order (latest answered)"),
        ("Orders with more than one review", one("select count(*) from (select order_id from raw.order_reviews "
                                                 "group by 1 having count(*) > 1)"), "as above"),
        ("Products with no category", one("select count(*) from raw.products where product_category_name is null"),
         "category = 'unknown'"),
        ("Categories with no English translation", one(
            "select count(distinct product_category_name) from raw.products where product_category_name is not null "
            "and product_category_name not in (select product_category_name from raw.category_translation)"),
         "Portuguese name kept"),
        ("Orders with no items", one("select count(*) from raw.orders o where not exists "
                                     "(select 1 from raw.order_items i where i.order_id = o.order_id)"),
         "order_value = 0; mostly canceled/unavailable"),
        ("Orders with no payment record", one("select count(*) from core.fct_orders where payment_total is null"),
         "kept; payment fields null"),
        ("'Delivered' orders with no delivery date", one(
            "select count(*) from raw.orders where order_status = 'delivered' and order_delivered_customer_date is null"),
         "is_delivered = false"),
        ("Valid orders whose payments differ from items + freight by > 1 BRL", one(
            "select count(*) from core.fct_orders where is_valid_sale and abs(payment_total - order_value) > 1"),
         "tracked by a dbt warning test (installment interest, vouchers)"),
        ("Customer IDs vs real people", one("select count(*) - count(distinct customer_unique_id) from raw.customers"),
         "customer_unique_id used as customer_key"),
        ("Geolocation rows (many per zip, some outside Brazil)", one("select count(*) from raw.geolocation"),
         "one median point per zip inside Brazil's bounding box"),
        ("Months with < 100 orders (start/end of data)", one(
            "select count(*) from analytics.mart_monthly_kpis where orders < 100"), "is_complete_month = false"),
    ]
    return pd.DataFrame(rows, columns=["issue", "count", "how it's handled"])


def all_findings(con=None) -> dict:
    con = con or connect()
    model = late_review_model(con)
    late_or = model.loc["late"]
    return {
        "growth": growth(con), "late_vs_review": late_vs_review(con),
        "late_model": {"n": model.attrs["n"], "odds_ratio_late": float(late_or.odds_ratio),
                       "ci": [float(late_or.ci_low), float(late_or.ci_high)], "p_value": float(late_or.p_value)},
        "monthly_correlation": monthly_late_review_correlation(con), "retention": retention(con),
        "sellers": sellers(con),
    }
