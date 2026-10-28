-- Level: medium
-- Question: The best-selling category (by item revenue) in each customer state.
-- Concepts: ROW_NUMBER() OVER (PARTITION BY ...), "top-N per group", QUALIFY
select customer_state as state,
       category,
       round(sum(item_price), 0) as revenue
from core.fct_order_items
where is_valid_sale
group by 1, 2
qualify row_number() over (partition by customer_state order by sum(item_price) desc) = 1
order by revenue desc
limit 12;
