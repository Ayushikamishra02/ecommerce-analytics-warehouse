-- Level: medium
-- Question: Cumulative (running) GMV through 2017, by month.
-- Concepts: SUM() OVER (ORDER BY ... ROWS UNBOUNDED PRECEDING)
select purchase_month as month,
       round(sum(order_value), 0)                                                   as gmv,
       round(sum(sum(order_value)) over (order by purchase_month
                                         rows between unbounded preceding and current row), 0) as running_gmv
from core.fct_orders
where is_valid_sale and year(purchase_month) = 2017
group by 1
order by 1;
