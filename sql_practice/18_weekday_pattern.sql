-- Level: easy
-- Question: Which weekday has the most orders, and does average order value change by weekday?
-- Concepts: join to a date dimension, ordering by a sort column instead of the label
select d.weekday_name,
       count(*)                     as orders,
       round(avg(o.order_value), 2) as aov
from core.fct_orders o
join core.dim_date d on d.date = o.purchase_date
where o.is_valid_sale
group by d.iso_weekday, d.weekday_name
order by d.iso_weekday;
