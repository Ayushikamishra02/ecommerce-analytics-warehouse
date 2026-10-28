-- Level: medium
-- Question: For each region, the category with the 2nd-highest revenue (the classic "Nth highest" question).
-- Concepts: DENSE_RANK vs ROW_NUMBER vs RANK (ties), join to a dimension for the region
with r as (
    select c.region, i.category, sum(i.item_price) as revenue
    from core.fct_order_items i
    join core.dim_customers c using (customer_key)
    where i.is_valid_sale
    group by 1, 2
)
select region, category, round(revenue, 0) as revenue
from r
qualify dense_rank() over (partition by region order by revenue desc) = 2
order by region;
