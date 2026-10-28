-- Item-level value summed per order must equal the order's value.
select o.order_id
from {{ ref('fct_orders') }} o
join (select order_id, sum(item_value) as v from {{ ref('fct_order_items') }} group by 1) i using (order_id)
where abs(o.order_value - i.v) > 0.01
