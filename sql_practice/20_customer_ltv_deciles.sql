-- Level: hard
-- Question: Split customers into 10 equal groups by lifetime spend. What share of revenue does each decile bring?
-- Concepts: NTILE, share of total
with c as (
    select customer_key, lifetime_value,
           ntile(10) over (order by lifetime_value desc) as decile
    from core.dim_customers
    where valid_orders >= 1
)
select decile,
       count(*)                                                         as customers,
       round(min(lifetime_value), 2)                                    as min_ltv,
       round(100 * sum(lifetime_value) / sum(sum(lifetime_value)) over (), 1) as pct_of_revenue
from c
group by 1
order by 1;
