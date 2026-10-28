-- Level: hard
-- Question: Build a monthly cohort table: for customers whose first order was in month X, what % ordered again
--           1, 2 and 3 months later? (First-half 2017 cohorts.)
-- Concepts: cohort assignment with MIN() OVER, month difference, conditional aggregation into columns (pivot)
with o as (
    select customer_key, purchase_month,
           min(purchase_month) over (partition by customer_key) as cohort_month
    from core.fct_orders
    where is_valid_sale
), activity as (
    select distinct customer_key, cohort_month,
           date_diff('month', cohort_month, purchase_month) as months_since
    from o
)
select cohort_month,
       count(distinct customer_key) filter (where months_since = 0)                       as cohort_size,
       round(100.0 * count(distinct customer_key) filter (where months_since = 1)
             / count(distinct customer_key) filter (where months_since = 0), 2)           as m1_pct,
       round(100.0 * count(distinct customer_key) filter (where months_since = 2)
             / count(distinct customer_key) filter (where months_since = 0), 2)           as m2_pct,
       round(100.0 * count(distinct customer_key) filter (where months_since = 3)
             / count(distinct customer_key) filter (where months_since = 0), 2)           as m3_pct
from activity
where cohort_month between '2017-01-01' and '2017-06-01'
group by 1
order by 1;
