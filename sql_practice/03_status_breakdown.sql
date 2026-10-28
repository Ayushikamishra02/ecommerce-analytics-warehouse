-- Level: easy
-- Question: How many orders are in each status, and what percent of all orders is that?
-- Concepts: COUNT(*), percentage of total with a window
select order_status,
       count(*)                                              as orders,
       round(100.0 * count(*) / sum(count(*)) over (), 2)    as pct
from core.fct_orders
group by 1
order by orders desc;
