# 05 · Power BI and DAX

The click-by-click build guide is in [powerbi/README.md](../../powerbi/README.md). This lesson explains the
concepts underneath, which is what interviews actually test.

## Why export a star schema, not one big table?

You could export one flat CSV with every column. It would work for a few visuals and then break:
filters on product category would not reach order-level measures cleanly, file sizes balloon (customer
attributes repeated on every row) and measures double count. Power BI's engine (VertiPaq) is designed for star
schemas: small dimension tables filter big fact tables through one-to-many relationships. The dbt marts are
already shaped that way, so the Power BI model is just the warehouse with relationships drawn in.

## Filter context: the one idea behind DAX

A measure is not a column. `GMV` has no value until a visual asks for it, and the visual decides **which rows
are visible**: the slicer selection, the row of the matrix (say, `region = "North"`), the bar of the chart
(`year_month = "2018-03"`). That set of filters is the **filter context**. The measure is evaluated fresh in every
cell, over only the rows that survive.

```DAX
GMV = CALCULATE ( SUM ( fct_orders[order_value] ), fct_orders[is_valid_sale] = TRUE () )
```

`CALCULATE` is the only function that *changes* filter context. Here it *adds* a filter (valid sales only) to
whatever the visual already applied. That is why one measure works on a card (all data), a monthly line (one
month per point) and a state map (one state per shape).

Two more patterns you will use constantly:

```DAX
-- REMOVE a filter: share of the total regardless of the seller selected
Seller GMV Share = DIVIDE ( [Item Revenue], CALCULATE ( [Item Revenue], ALL ( dim_sellers ) ) )

-- SHIFT a filter: same period last year (needs a date table)
GMV PY = CALCULATE ( [GMV], SAMEPERIODLASTYEAR ( dim_date[date] ) )
```

## Measures vs calculated columns

| | Calculated column | Measure |
|---|---|---|
| Computed | once, at refresh, per row | at query time, per visual cell |
| Stored | yes (uses memory) | no |
| Use for | slicing/grouping (`Lateness Bucket`) | numbers you aggregate (`Late Rate`) |
| Example mistake | `Late Rate` as a column, then averaging it | a bucket as a measure: can't go on an axis |

Rule of thumb: if you want to *put it on an axis or a slicer*, it's a column. If you want to *show it as a
number*, it's a measure.

## `DIVIDE` and blanks

`DIVIDE(a, b)` returns blank instead of an error when `b` is 0 or blank, so a month with no deliveries shows an
empty cell instead of `Infinity`. Blank also means "don't plot this point", which is usually what you want.

## Why `dim_date` must be marked as a date table

Time-intelligence functions (`SAMEPERIODLASTYEAR`, `TOTALYTD`, `DATESINPERIOD`) need a table with one row per day
and no gaps. `fct_orders[purchase_date]` has gaps (days with no orders) and duplicates; `dim_date` (a date spine
from dbt) has neither. Marking it tells Power BI to use it for all date logic.

## Matching the warehouse

The measure file lists the value each measure should show with no filters. If your card for `Valid Orders`
shows 99,441 instead of 98,207, the `is_valid_sale` filter is missing; if `Customers` shows 99,441, you counted
`customer_id` instead of `customer_key`. Checking BI numbers against the warehouse *before* building visuals is a
habit worth mentioning in interviews: it is how analytics teams keep finance and dashboards in agreement.

## Design rules used in the guide

1. **Titles state the finding**, not the chart type: "Late orders get 1–2 stars 63% of the time" beats
   "Bad review rate by lateness bucket".
2. **Five KPI cards maximum** across the top; each with a comparison (vs last year, vs target) if you have one.
3. **One question per page**: overview, delivery, customers, sellers.
4. **Same slicers on every page**, synced, on the left.
5. **Colour means something**: red only for "bad" (late, low rating); don't use the default rainbow for categories.

## Interview questions on this topic

- *What is filter context? Row context?* Filter context = which rows a measure sees in a given cell. Row context =
  "the current row" while iterating (in a calculated column or inside `SUMX`); it does not filter other tables
  unless converted with `CALCULATE` (context transition).
- *Why might a measure show the same value in every row of a matrix?* The rows' column isn't connected to the
  measure's table (missing or inactive relationship), or the measure uses `ALL()`.
- *Import vs DirectQuery?* Import copies data into the model (fast, needs refresh); DirectQuery sends SQL to the
  source on every interaction (always fresh, slower, some DAX limits). For this project: Import.
- *How would you refresh this daily?* Publish to Power BI Service, set up a gateway or cloud source (e.g. the dbt
  output in a cloud warehouse), schedule refresh after the dbt job finishes.

Next: [06 · SQL interview practice](06_sql_interview_practice.md)
