-- Level: medium
-- Question: Late-delivery rate and average review score per state, for states with 500+ delivered orders.
-- Concepts: conditional aggregation (AVG of a boolean), HAVING
select customer_state as state,
       count(*)                                  as delivered_orders,
       round(100 * avg(is_late::int), 1)         as late_pct,
       round(avg(delivery_days), 1)              as avg_delivery_days,
       round(avg(review_score), 2)               as avg_review
from core.fct_orders
where is_delivered
group by 1
having count(*) >= 500
order by late_pct desc;
