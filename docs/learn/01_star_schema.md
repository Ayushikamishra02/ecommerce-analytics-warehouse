# 01 · The star schema

## The problem with the raw data

Olist ships 9 CSV files that mirror how the *application* stores data, not how an *analyst* asks questions:

```
orders ─┬─ order_items ── products ── category_translation
        ├─ order_payments          └─ sellers ── geolocation
        ├─ order_reviews
        └─ customers ── geolocation
```

To answer "average review score of late orders in the Northeast, by product category", you would join
orders → customers (state) → a region lookup → order_items → products → translation, plus reviews, and handle
duplicate reviews, orders with several items in different categories, and orders without items. Every analyst
would do it slightly differently and get slightly different numbers. That is the real problem a warehouse solves:
**one agreed, tested version of the joins and definitions**.

## Facts and dimensions

A **star schema** splits tables into two kinds:

- **Fact table**: one row per *event* you measure. Mostly keys and numbers (money, counts, durations, flags).
  Long and narrow. Here: `fct_orders` (one row per order) and `fct_order_items` (one row per item in an order).
- **Dimension table**: one row per *thing* that describes events. Mostly text attributes you filter and group
  by. Short and wide. Here: `dim_customers`, `dim_products`, `dim_sellers`, `dim_date`.

```
                 dim_date
                    │
dim_customers ── fct_orders            dim_products
                    │                      │
                 (order_id)         fct_order_items ── dim_sellers
                                           │
                                       dim_date, dim_customers
```

Draw it with the fact in the middle and the dimensions around it, and it looks like a star. Queries become
"filter the dimensions, aggregate the fact" which is easy to write, easy to read, and fast.

## Grain: the most important word

The **grain** is what one row of a fact table means. Write it down before writing any SQL:

| Table | Grain | Example question it answers |
|---|---|---|
| `fct_orders` | one order | late rate, AOV, review score per order |
| `fct_order_items` | one item line within an order | revenue by category, by seller, by product |

Why two facts? Because questions live at different grains. Review scores belong to orders (a customer reviews the
order, not each item). Category and seller belong to items (one order can contain items from 2 categories and 2
sellers). If you force everything into one table, you get one of two bugs:

- Put item rows in the order fact → the review score repeats once per item, and `avg(review_score)` over-weights
  big orders.
- Put orders in the item fact without care → `sum(freight)` double counts freight that belongs to the order.

`fct_orders` still carries `main_category` (the category of the order's most expensive item) and `n_sellers` as
*convenience* columns, clearly documented as summaries.

**Rule:** never join two fact tables directly. Go through a shared dimension (date, customer). Joining
`fct_orders` to `fct_order_items` on `order_id` and then summing `order_value` multiplies each order by its number
of items. Question 17 in the SQL lesson shows the safe pattern (aggregate each child first, then join).

## Keys

- `customer_key` = `customer_unique_id`. Olist's `customer_id` is **per order** (99,441 of them for 96,096
  people). Using it as "the customer" makes repeat purchase look like 0%. Choosing the right key is a modelling
  decision with business consequences; it is documented in `_core.yml` and tested (`unique` on
  `dim_customers.customer_key`, `relationships` from the fact).
- `dim_date` is generated (a *date spine*: every day from 2016-09-01 to 2018-10-31) rather than taken from orders,
  so days with zero orders still exist. That is what lets SQL question 21 find gaps.

## Denormalisation is on purpose

`fct_orders` contains `customer_state` and `customer_region` even though they also live in `dim_customers`. In
an application database that would be a mistake (two places to update). In an analytical model it is a deliberate
trade: the fact is rebuilt from scratch every run, so the copies cannot drift, and the most common filters need
no join. Kimball (the classic book on this: *The Data Warehouse Toolkit*) calls these *degenerate* or
*denormalised* attributes.

## Slowly changing dimensions (what we did not need)

If a seller moves state, should old orders show the old state? That is a *slowly changing dimension*:
Type 1 overwrites (history lost), Type 2 adds a new row with valid-from/valid-to dates (history kept). The Olist
snapshot has one address per seller, so every dimension here is Type 1. Interviewers like this question; dbt
implements Type 2 with **snapshots**.

## Check yourself

1. What is the grain of `mart_monthly_kpis`? *(one month)*
2. Why does `fct_order_items` carry `customer_key` and `purchase_date`? *(so it can be filtered by the customer and
   date dimensions directly, without passing through the order fact)*
3. A colleague computes AOV as `avg(item_price)` from `fct_order_items`. What is wrong? *(that is average item
   price, not average order value: orders with 3 items count 3 times, and freight is missing)*

Next: [02 · dbt and the warehouse layers](02_dbt_warehouse.md)
