-- Level: easy
-- Question: Top 10 product categories by item revenue, with their share of total revenue.
-- Concepts: aggregate, window function over the whole result (sum() over ())
select category,
       round(sum(item_price), 0)                                          as revenue,
       round(100 * sum(item_price) / sum(sum(item_price)) over (), 2)     as pct_of_total
from core.fct_order_items
where is_valid_sale
group by 1
order by revenue desc
limit 10;
