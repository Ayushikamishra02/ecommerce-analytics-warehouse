-- Level: easy
-- Question: Monthly GMV and number of valid orders, for complete months only.
-- Concepts: GROUP BY, FILTER on a flag, date_trunc
select purchase_month as month,
       count(*)                     as orders,
       round(sum(order_value), 2)   as gmv
from core.fct_orders
where is_valid_sale
  and purchase_month between '2017-01-01' and '2018-08-01'
group by 1
order by 1;
