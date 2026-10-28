"""Olist e-commerce dashboard, reading straight from the DuckDB warehouse.

    olist build            # once
    streamlit run app/streamlit_app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from olistwh.warehouse import connect  # noqa: E402

st.set_page_config(page_title="Olist e-commerce warehouse", layout="wide")
BLUE, ORANGE, RED, GREEN, PURPLE = "#4C72B0", "#DD8452", "#C44E52", "#55A868", "#8172B3"
REGION_COLORS = {"Southeast": BLUE, "South": GREEN, "Center-West": PURPLE, "Northeast": ORANGE, "North": RED}


@st.cache_resource
def con():
    return connect()


@st.cache_data
def q(sql: str, params: tuple = ()) -> pd.DataFrame:
    return con().execute(sql, list(params)).df()


try:
    con()
except FileNotFoundError:
    st.error("Warehouse not found. Run `olist build` first (downloads the data and runs dbt, ~1 minute).")
    st.stop()

# ---------------------------------------------------------------------------------------------------- filters
months = q("select distinct purchase_month from core.fct_orders "
           "where purchase_month between '2017-01-01' and '2018-08-01' order by 1")["purchase_month"]
labels = [m.strftime("%Y-%m") for m in months]
regions = q("select distinct region from core.dim_customers where region is not null order by 1")["region"].tolist()
cats = q("select main_category, count(*) n from core.fct_orders where main_category is not null "
         "group by 1 order by n desc")["main_category"].tolist()

with st.sidebar:
    st.header("Filters")
    start, end = st.select_slider("Purchase month", options=labels, value=(labels[0], labels[-1]))
    sel_regions = st.multiselect("Customer region", regions, default=regions)
    sel_cats = st.multiselect("Main product category (blank = all)", cats, default=[])
    st.caption("Complete months only (Jan 2017 - Aug 2018). GMV = items + freight on valid (not canceled / "
               "unavailable) orders. Data: Olist public dataset.")

where = ["o.purchase_month between ?::date and ?::date", "o.customer_region in (select unnest(?::varchar[]))"]
params: list = [f"{start}-01", f"{end}-01", sel_regions or regions]
if sel_cats:
    where.append("o.main_category in (select unnest(?::varchar[]))")
    params.append(sel_cats)
W = " and ".join(where)


def qf(sql: str) -> pd.DataFrame:
    """Query with the sidebar filters applied (`{W}` in the SQL is replaced by the filter clause)."""
    return q(sql.replace("{W}", W), tuple(params))


# ---------------------------------------------------------------------------------------------------- KPIs
st.title("Olist e-commerce dashboard")
st.caption("Brazilian marketplace, 2017-2018 · DuckDB + dbt warehouse")
k = qf("""
    select count(*) filter (where is_valid_sale)                                  as orders,
           sum(order_value) filter (where is_valid_sale)                          as gmv,
           count(distinct customer_key) filter (where is_valid_sale)              as customers,
           avg(is_late::int) filter (where is_delivered)                          as late_rate,
           avg(review_score)                                                      as avg_review,
           avg(is_bad_review::int) filter (where is_delivered)                    as bad_rate,
           avg(delivery_days) filter (where is_delivered)                         as delivery_days
    from core.fct_orders o where {W}""").iloc[0]
if not k["orders"]:
    st.warning("No orders match these filters.")
    st.stop()
c = st.columns(6)
c[0].metric("GMV", f"R${k.gmv / 1e6:,.1f}M")
c[1].metric("Orders", f"{k.orders:,.0f}")
c[2].metric("Avg order", f"R${k.gmv / k.orders:,.0f}")
c[3].metric("Avg delivery", f"{k.delivery_days:.1f} days")
c[4].metric("Late deliveries", f"{k.late_rate:.1%}")
c[5].metric("Avg review", f"{k.avg_review:.2f} ★", help=f"{k.bad_rate:.1%} of delivered orders got 1-2 stars")

tab1, tab2, tab3, tab4 = st.tabs(["Sales", "Delivery & reviews", "Customers", "Sellers"])

# ---------------------------------------------------------------------------------------------------- sales
with tab1:
    m = qf("""select purchase_month as month, sum(order_value) as gmv, count(*) as orders
              from core.fct_orders o where is_valid_sale and {W} group by 1 order by 1""")
    m["aov"] = m.gmv / m.orders
    fig = go.Figure()
    fig.add_bar(x=m.month, y=m.gmv, name="GMV", marker_color=BLUE)
    fig.add_scatter(x=m.month, y=m.aov, name="Avg order value", yaxis="y2", line_color=ORANGE)
    fig.update_layout(title="Monthly GMV and average order value", height=380, legend_orientation="h",
                      yaxis_title="GMV (R$)", yaxis2={"overlaying": "y", "side": "right", "title": "AOV (R$)",
                                                      "rangemode": "tozero"})
    st.plotly_chart(fig, width="stretch")
    a, b = st.columns(2)
    cat = qf("""select coalesce(main_category, 'unknown') as category, sum(order_value) as gmv
                from core.fct_orders o where is_valid_sale and {W} group by 1 order by gmv desc limit 12""")
    a.plotly_chart(px.bar(cat.iloc[::-1], x="gmv", y="category", orientation="h", title="Top categories by GMV",
                          color_discrete_sequence=[BLUE]).update_layout(height=420), width="stretch")
    pay = qf("""select coalesce(payment_type, 'none') as payment_type, count(*) as orders
                from core.fct_orders o where is_valid_sale and {W} group by 1""")
    b.plotly_chart(px.pie(pay, names="payment_type", values="orders", hole=0.5, title="Payment method (orders)",
                          color_discrete_sequence=[BLUE, ORANGE, GREEN, PURPLE, "#8C8C8C"])
                   .update_layout(height=420), width="stretch")

# ---------------------------------------------------------------------------------------------------- delivery
with tab2:
    d = qf("""
        select case when days_late <= -10 then 1 when days_late <= -5 then 2 when days_late <= 0 then 3
                    when days_late <= 3 then 4 when days_late <= 7 then 5 when days_late <= 14 then 6 else 7 end as k,
               count(*) as orders, avg(is_bad_review::int) as bad_review_rate, avg(review_score) as avg_review
        from core.fct_orders o where is_delivered and has_review and {W} group by 1 order by 1""")
    names = {1: "10+ days early", 2: "5-9 early", 3: "0-4 early", 4: "1-3 late", 5: "4-7 late", 6: "8-14 late",
             7: "15+ late"}
    d["arrival"] = d.k.map(names)
    a, b = st.columns(2)
    a.plotly_chart(px.bar(d, x="arrival", y="bad_review_rate", text_auto=".0%", hover_data=["orders", "avg_review"],
                          color=d.k > 3, color_discrete_map={False: GREEN, True: RED},
                          title="Share of 1-2 star reviews by arrival vs promised date")
                   .update_layout(showlegend=False, yaxis_tickformat=".0%", height=400), width="stretch")
    mm = qf("""select purchase_month as month, avg(is_late::int) as late_rate, avg(is_bad_review::int) as bad_review_rate
               from core.fct_orders o where is_delivered and {W} group by 1 order by 1""")
    b.plotly_chart(px.line(mm, x="month", y=["late_rate", "bad_review_rate"], markers=True,
                           color_discrete_sequence=[RED, PURPLE], title="Late deliveries and bad reviews by month")
                   .update_layout(yaxis_tickformat=".0%", height=400, legend_title=""), width="stretch")
    s = qf("""select customer_state as state, customer_region as region, count(*) as orders,
                     avg(delivery_days) as avg_delivery_days, avg(is_late::int) as late_rate,
                     avg(review_score) as avg_review
              from core.fct_orders o where is_delivered and {W} group by 1, 2 having count(*) >= 30""")
    st.plotly_chart(px.scatter(s, x="avg_delivery_days", y="avg_review", size="orders", color="region", text="state",
                               color_discrete_map=REGION_COLORS,
                               hover_data={"late_rate": ":.1%"},
                               title="Each bubble is a state: slower delivery, lower ratings")
                    .update_traces(textposition="top center").update_layout(height=450), width="stretch")

# ---------------------------------------------------------------------------------------------------- customers
with tab3:
    st.caption("Retention and RFM use each customer's full history, so only the region filter applies here.")
    reg = tuple(sel_regions or regions)
    coh = q("""select r.cohort_month, r.months_since, sum(r.active_customers) / sum(r.cohort_size) as rate
               from analytics.mart_cohort_retention r
               where r.cohort_month between '2017-01-01' and '2018-06-01' and r.months_since between 1 and 12
               group by 1, 2 order by 1, 2""")
    piv = coh.pivot(index="cohort_month", columns="months_since", values="rate")
    piv.index = [i.strftime("%Y-%m") for i in piv.index]
    fig = px.imshow(piv * 100, color_continuous_scale="Blues", aspect="auto", text_auto=".1f",
                    labels={"x": "months after first order", "y": "cohort", "color": "% active"},
                    title="Cohort retention (% of each cohort ordering again), all regions")
    st.plotly_chart(fig.update_layout(height=520), width="stretch")
    rfm = q("""select r.segment, count(*) as customers, sum(r.monetary) as revenue
               from analytics.mart_rfm r join core.dim_customers c using (customer_key)
               where c.region in (select unnest(?::varchar[])) group by 1""", (list(reg),))
    rfm["customer share"] = rfm.customers / rfm.customers.sum()
    rfm["revenue share"] = rfm.revenue / rfm.revenue.sum()
    long = rfm.melt(id_vars="segment", value_vars=["customer share", "revenue share"])
    st.plotly_chart(px.bar(long, x="value", y="segment", color="variable", barmode="group", orientation="h",
                           color_discrete_sequence=["#8C8C8C", BLUE], title="RFM segments")
                    .update_layout(xaxis_tickformat=".0%", height=420, legend_title=""), width="stretch")

# ---------------------------------------------------------------------------------------------------- sellers
with tab4:
    sp = q("select * from analytics.mart_seller_performance order by gmv_rank")
    sp["pct_sellers"] = sp.gmv_rank / len(sp)
    a, b = st.columns([1, 1])
    fig = px.line(sp, x="pct_sellers", y="cumulative_gmv_share", title="Seller concentration (all data)")
    fig.add_hline(y=0.8, line_dash="dot", line_color=RED)
    a.plotly_chart(fig.update_layout(xaxis_tickformat=".0%", yaxis_tickformat=".0%", height=400),
                   width="stretch")
    min_orders = b.slider("Minimum orders", 10, 200, 30)
    max_rating = b.slider("Show sellers averaging below (stars)", 2.0, 5.0, 3.5, 0.1)
    flagged = sp[(sp.orders >= min_orders) & (sp.avg_review_score < max_rating)]
    b.metric("Sellers flagged", len(flagged), help="busy sellers with low average ratings")
    b.dataframe(flagged[["seller_id", "seller_state", "orders", "gmv", "avg_review_score", "late_rate"]]
                .sort_values("gmv", ascending=False).round(3), height=260, width="stretch")
