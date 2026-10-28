-- Level: medium
-- Question: Month-over-month GMV growth (%) for complete months.
-- Concepts: CTE, LAG window function
with m as (
    select purchase_month as month, sum(order_value) as gmv
    from core.fct_orders
    where is_valid_sale and purchase_month between '2017-01-01' and '2018-08-01'
    group by 1
)
select month,
       round(gmv, 0)                                                  as gmv,
       round(100 * (gmv / lag(gmv) over (order by month) - 1), 1)     as mom_growth_pct
from m
order by month;
