-- Level: medium
-- Question: Daily orders and the 7-day moving average around Black Friday 2017 (Nov 17 - Dec 1).
-- Concepts: date spine (so days with zero orders are not skipped), LEFT JOIN, AVG() OVER with a ROWS frame
with daily as (
    select d.date, count(o.order_id) as orders
    from core.dim_date d
    left join core.fct_orders o on o.purchase_date = d.date and o.is_valid_sale
    where d.date between '2017-11-01' and '2017-12-01'
    group by 1
)
select date,
       orders,
       round(avg(orders) over (order by date rows between 6 preceding and current row), 1) as orders_7d_avg
from daily
qualify date >= '2017-11-17'
order by date;
