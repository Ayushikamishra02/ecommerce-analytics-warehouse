-- Level: medium
-- Question: For customers who came back, how many days passed between their 1st and 2nd order?
-- Concepts: ROW_NUMBER to number each customer's orders, self-join (or LEAD), percentiles
with numbered as (
    select customer_key, purchased_at,
           lead(purchased_at) over (partition by customer_key order by purchased_at) as next_at,
           row_number()       over (partition by customer_key order by purchased_at) as n
    from core.fct_orders
    where is_valid_sale
)
select count(*)                                                               as customers_with_2nd_order,
       round(avg(date_diff('day', purchased_at, next_at)), 1)                 as avg_days,
       quantile_cont(date_diff('day', purchased_at, next_at), 0.5)            as median_days,
       round(100.0 * avg((date_diff('day', purchased_at, next_at) = 0)::int), 1) as pct_same_day
from numbered
where n = 1 and next_at is not null;
