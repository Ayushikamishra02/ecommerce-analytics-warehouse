-- Level: hard
-- Question: How many sellers (and what % of sellers) together make 80% of item revenue?
-- Concepts: cumulative share with a window, then pick the first row that crosses 80%
-- Takeaway: ~18% of sellers make 80% of item revenue (the dbt mart says 558 sellers using items + freight; 540 here on items only: always state which revenue definition you used).
with s as (
    select seller_id, sum(item_price) as revenue
    from core.fct_order_items
    where is_valid_sale
    group by 1
), ranked as (
    select seller_id, revenue,
           row_number() over (order by revenue desc)                         as rnk,
           sum(revenue) over (order by revenue desc rows unbounded preceding)
             / sum(revenue) over ()                                          as cum_share,
           count(*) over ()                                                  as n_sellers
    from s
)
select rnk                               as sellers_needed,
       n_sellers,
       round(100.0 * rnk / n_sellers, 1) as pct_of_sellers,
       round(100 * cum_share, 2)         as cum_revenue_pct
from ranked
where cum_share >= 0.8
order by rnk
limit 1;
