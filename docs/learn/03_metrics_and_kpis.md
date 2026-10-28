# 03 · Metrics and KPI definitions

A KPI is only useful if two people computing it get the same number. Most analytics arguments are really
arguments about definitions: *which orders? which date? which denominator?* This lesson writes each one down the
way a metrics layer (or a "metric dictionary" page in a company wiki) would.

## The dictionary

| Metric | Definition | Where | Value (all data / complete months) |
|---|---|---|---|
| **Valid order** | `order_status not in ('canceled', 'unavailable')` | `fct_orders.is_valid_sale` | 98,207 |
| **GMV** | sum of item price + freight over valid orders | `mart_monthly_kpis.gmv` | R$15.74M / R$15.68M |
| **AOV** | GMV / valid orders | `avg_order_value` | R$160 |
| **Customers** | distinct `customer_key` (= `customer_unique_id`) with a valid order | `dim_customers` | 94,990 |
| **Delivered order** | status `delivered` **and** a delivery timestamp exists | `is_delivered` | 96,470 |
| **Delivery time** | purchase timestamp → delivered timestamp, in days | `delivery_days` | 12.6 days avg |
| **Late** | delivered on a later *calendar day* than the estimated date | `is_late` | 6.8% of delivered |
| **Days late** | delivered date − estimated date (negative = early) | `days_late` | |
| **Bad review** | review score ≤ `var('bad_review_max_stars')` (2) | `is_bad_review` | 13.2% of delivered |
| **Repeat rate** | customers with 2+ valid orders / customers with 1+ | `mart_rfm.frequency` | 3.04% |
| **Cohort retention (month k)** | of customers whose first valid order was in month M, the share with a valid order in month M+k | `mart_cohort_retention` | ~0.5% at k = 1 |
| **Freight share** | freight / (items + freight) | `mart_state_delivery` | 14.2% |
| **Complete month** | Jan 2017 – Aug 2018 (outside: < 100 orders/month, collection ramp-up and cut-off) | `is_complete_month` | 20 months |

## The traps, with real numbers from this data

**1. GMV is not revenue.** Olist is a marketplace: sellers own the goods; Olist earns a commission and fees we
don't see. Calling R$15.7M "revenue" in an interview is a red flag. Say *GMV* (or "gross merchandise value
through the platform").

**2. Partial periods.** The data has 2 orders in September 2016 and 1 in September 2018. Any "month over month"
or "average month" that includes them is nonsense. The fix is a flag (`is_complete_month`) and charts that grey out
partial months, rather than silently deleting data.

**3. Same-period comparison.** Comparing 2018 (8 months) with 2017 (12 months) understates growth; comparing
Jan–Aug 2018 with Jan–Aug 2017 is fair: GMV **+140%**, orders **+137%**. Growth also has seasonality: November
2017 (Black Friday) is the biggest month, so "Dec vs Nov" always looks like a decline.

**4. The wrong id.** `customer_id` is generated per order. Counting it gives 99,441 "customers" who each ordered
exactly once, so repeat rate = 0%. The person is `customer_unique_id`: 96,096 people, of whom 2,888 (3.04%)
bought twice or more.

**5. Denominators.** "Late rate" could mean late / all orders, late / shipped, or late / delivered. Undelivered
orders can't be late or on time yet, so the denominator is **delivered** orders. Write it down; dashboards
disagree most often on denominators.

**6. Averages hide mix.** AOV barely moved (R$158 → R$161) while GMV grew 140%: growth came from *more orders*,
not bigger baskets. But AOV is also sensitive to category mix: a month with more furniture has a higher AOV with
no change in customer behaviour. When an average moves, check whether the mix moved.

**7. Calendar day vs timestamp.** `is_late` compares *dates*. A parcel promised for the 10th and delivered at
08:00 on the 10th is on time; comparing timestamps would call it late because every estimate is stored as midnight.
Small choice, big effect: comparing timestamps gives a late rate of 8.1% instead of 6.8%.

**8. Order-level vs item-level.** "Average review of the health_beauty category" can be computed per order (each
review counts once) or per item (orders with 3 items count 3 times). Both are defensible; they give different
numbers. Pick one, label it.

**9. Survivorship in reviews.** The public dataset only includes orders that received a review survey (every order
in it has a review). Real-world review coverage would be lower, and the customers who don't answer may differ.
State this limitation instead of hiding it.

## Retention: three definitions, three numbers

| Definition | Number | When to use |
|---|---|---|
| Ever repurchased (repeat rate) | 3.04% | simplest headline |
| Month-1 cohort retention, 2017 cohorts | 0.52% | product/marketing teams tracking a "return next month" goal |
| Median days to second order (repeaters only) | 28 days; 30% on the *same day* | CRM timing: when to send the reminder |

The same-day 30% is worth noticing: many "repeat purchases" are a customer placing two orders minutes apart
(different sellers, or a forgotten item), not a returning customer. A stricter repeat definition would exclude
same-day second orders.

## RFM in one paragraph

RFM scores each customer on **R**ecency (days since last order), **F**requency (orders) and **M**onetary (spend),
then names segments. The textbook version uses quintiles for all three, but 97% of customers have exactly one
order, so frequency quintiles are meaningless; here F is 1 vs 2+ orders and R and M are quintiles
(`mart_rfm.sql`). The segment rules are business choices, written in SQL so they can be argued about:
*Champions* (2+ orders, recent), *New big spenders* (1 order, recent, top-40% spend), *At risk, high value* (1
order, old, top-40% spend), and so on.

## Check yourself

1. Sales say "AOV dropped 8% in December, the new checkout is broken". What two things do you check first?
   *(Category mix and whether December is complete/compared to the right baseline; then the number of items per
   order.)*
2. Why can't late rate be computed for status `shipped`? *(No delivery date yet; it is censored, not on time.)*
3. Which metric changes if you switch `customer_key` to `customer_id`? *(Repeat rate, cohort retention, customer
   counts, RFM; not GMV or orders.)*

Next: [04 · Analysis and statistics](04_analysis_and_statistics.md)
