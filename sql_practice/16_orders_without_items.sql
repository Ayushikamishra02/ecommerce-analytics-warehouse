-- Level: easy
-- Question: Find orders that have no items at all, grouped by status. Two ways: LEFT JOIN ... IS NULL, and NOT EXISTS.
-- Concepts: anti-join
select o.order_status, count(*) as orders_without_items
from raw.orders o
left join raw.order_items i on i.order_id = o.order_id
where i.order_id is null
group by 1
order by 2 desc;
-- Same result with NOT EXISTS (often faster, never duplicates rows):
-- select order_status, count(*) from raw.orders o
-- where not exists (select 1 from raw.order_items i where i.order_id = o.order_id) group by 1;
