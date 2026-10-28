# Power BI dashboard: build guide

A `.pbix` file is binary and can only be made in Power BI Desktop (Windows, free), so this folder holds everything
needed to build it yourself in about an hour, plus the numbers to check it against. Building it is good practice:
"connect, model, measure, visualise" is exactly what analyst interviews ask about.

| File | What it is |
|---|---|
| `data/*.parquet` | the star schema + three marts, created by `olist powerbi` (git-ignored, 20 MB) |
| `measures.dax` | every measure, each with the value you should see with no filters |
| `olist_theme.json` | colours and fonts matching the README figures |
| `README.md` | this guide: model, pages, checks |

If you are on a Mac, the same steps work in Tableau Public or Looker Studio (import the Parquet or CSVs);
only the DAX changes.

---

## 1. Load the data (5 min)

1. `olist build` then `olist powerbi` (creates `powerbi/data/`).
2. Power BI Desktop → **Get data → Parquet** → pick `fct_orders.parquet` → **Load**. Repeat for every file in
   `powerbi/data/` (or **Get data → Folder** and combine, but one query per file is clearer to learn with).
3. **View → Themes → Browse for themes** → `olist_theme.json`.

## 2. Model view: the star schema (10 min)

Open **Model view** and make these relationships (drag the column from the fact onto the dimension). Power BI may
auto-detect some; delete any it guesses that are not on this list.

| From (many side) | To (one side) | Notes |
|---|---|---|
| `fct_orders[purchase_date]` | `dim_date[date]` | active |
| `fct_orders[customer_key]` | `dim_customers[customer_key]` | |
| `fct_order_items[purchase_date]` | `dim_date[date]` | |
| `fct_order_items[customer_key]` | `dim_customers[customer_key]` | |
| `fct_order_items[product_id]` | `dim_products[product_id]` | |
| `fct_order_items[seller_id]` | `dim_sellers[seller_id]` | |
| `mart_rfm[customer_key]` | `dim_customers[customer_key]` | one-to-one |
| `mart_seller_performance[seller_id]` | `dim_sellers[seller_id]` | one-to-one |

All single direction (dimension filters fact). Then:

- Select `dim_date` → **Table tools → Mark as date table** → column `date`. Time-intelligence DAX
  (`SAMEPERIODLASTYEAR`, `TOTALMTD`) needs this.
- **Do not** connect `fct_orders` to `fct_order_items` directly. Two facts talk to each other only through shared
  dimensions (date, customer). Joining facts creates many-to-many relationships and double counting: a classic
  interview question.
- Hide the key columns in the facts (right-click → Hide in report view) so report builders use the dimension
  columns for slicers.
- Sort `dim_date[month_name]` by `dim_date[month]` (Column tools → Sort by column).

Why a star? Each fact row is one event (an order, an order line); each dimension row describes one thing (a
customer, a product). Filters flow from the small tables to the big one, which is fast and easy to reason about.
See [lesson 01](../docs/learn/01_star_schema.md).

## 3. Measures (15 min)

Home → **Enter data** → name the table `_Measures` → Load. Then for each block in `measures.dax`:
select `_Measures` → **New measure** → paste. Delete the dummy column afterwards; the table icon changes to a
calculator.

Format: GMV / AOV as currency (R$, 0 decimals for GMV), rates as percentage (1 decimal).

Add one **calculated column** to `fct_orders` (Table tools → New column) for the delivery chart:

```DAX
Lateness Bucket =
SWITCH (
    TRUE (),
    ISBLANK ( fct_orders[days_late] ), BLANK (),
    fct_orders[days_late] <= -10, "a) 10+ days early",
    fct_orders[days_late] <= -5,  "b) 5-9 days early",
    fct_orders[days_late] <= 0,   "c) 0-4 days early",
    fct_orders[days_late] <= 3,   "d) 1-3 days late",
    fct_orders[days_late] <= 7,   "e) 4-7 days late",
    fct_orders[days_late] <= 14,  "f) 8-14 days late",
    "g) 15+ days late"
)
```

(The letter prefix keeps the axis in order without a sort table. Same cut points as `mart_delivery_vs_review`.)

### Check before building visuals

Drop a **Card** for each of these with no filters. If one is off, the relationship or a filter in the measure is
wrong; fix it now, not after ten visuals.

| Measure | Expected |
|---|---|
| Valid Orders | 98,207 |
| GMV | R$ 15.74M |
| AOV | R$ 160.23 |
| Customers | 94,990 |
| Late Rate | 6.8% |
| Bad Review Rate \| Late / \| On Time | 62.9% / 9.5% |
| Repeat Customer Rate | 3.0% |
| Active Sellers | 3,053 |

## 4. Pages (30 min)

Canvas 1280 × 720. Every page gets the same slicer strip on the left: `dim_date[year_month]` (between),
`dim_customers[region]`, `dim_products[category]`. Use **View → Sync slicers** so they apply to all pages.

### Page 1 · Overview

| Visual | Fields |
|---|---|
| 5 cards (top row) | GMV · Valid Orders · AOV · Late Rate · Avg Review Score |
| Line + clustered column | X `dim_date[year_month]`, columns `GMV`, line `AOV` (secondary axis) |
| Bar (top 10) | Y `dim_products[category]`, X `Item Revenue`, Top N filter = 10 |
| Filled map / shape map | Location `dim_customers[state]` (set Data category = State or Province, add "Brazil" via a calculated column if Bing guesses wrong), colour `GMV` |

Title idea: *"GMV up 140% year on year; average basket flat at ~R$160"*. Titles that state the finding beat
titles that name the chart.

### Page 2 · Delivery and reviews

| Visual | Fields |
|---|---|
| Clustered column | X `fct_orders[Lateness Bucket]`, Y `Bad Review Rate`, data labels on |
| Line chart | X `dim_date[year_month]`, Y `Late Rate` and `Bad Review Rate` |
| Matrix | Rows `dim_customers[region]` → `state`, values `Avg Delivery Days`, `Late Rate`, `Avg Review Score`; conditional formatting → background colour scale |
| Scatter | Details `dim_customers[state]`, X `Late Rate`, Y `Avg Review Score`, size `Delivered Orders` |

Title idea: *"Late orders get 1-2 stars 63% of the time (vs 9.5% on time)"*.

### Page 3 · Customers

| Visual | Fields |
|---|---|
| Matrix (heatmap) | Rows `mart_cohort_retention[cohort_month]`, columns `months_since` (filter 1-12), values `Cohort Retention %`, background colour scale |
| Clustered bar | Y `mart_rfm[segment]`, X count of `customer_key` and sum of `monetary` (show as % of grand total) |
| Card | Repeat Customer Rate |

Title idea: *"97% of customers buy once; retention, not acquisition, is the gap"*.

### Page 4 · Sellers

| Visual | Fields |
|---|---|
| Line | X `mart_seller_performance[gmv_rank]`, Y `cumulative_gmv_share`, add a constant line at 0.8 |
| Table | `seller_id`, `seller_state`, `orders`, `gmv`, `avg_review_score`, `late_rate`; visual filter `orders >= 30` and `avg_review_score < 3.5` |
| Card | Active Sellers |

Title idea: *"18% of sellers make 80% of GMV; 39 busy sellers average under 3.5 stars"*.

## 5. Finish

- Add a **tooltip page** (Page information → Allow use as tooltip) showing Late Rate and Avg Review Score for
  the hovered state.
- **Bookmarks + buttons** for "Southeast only" / "All Brazil" are a nice touch in a demo.
- Performance Analyzer (View tab) → record → refresh visuals: everything should render in < 1 s; if a visual is
  slow, the usual cause is a measure iterating over the item fact.
- File → Export → PDF, and take screenshots for the repo README (`docs/powerbi/` is a good place).
- To share online, Publish to Power BI Service (needs a work/school account) or record a 60-second walkthrough GIF.
