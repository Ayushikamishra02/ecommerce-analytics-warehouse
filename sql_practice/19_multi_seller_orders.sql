-- Level: medium
-- Question: Are orders with items from more than one seller more likely to be late or get a bad review?
-- Concepts: bucketing with CASE, comparing rates across groups
-- Takeaway: Multi-seller orders are recorded as arriving EARLIER, yet get 1-2 stars ~4x as often (48% vs 13%; still 2x when you compare only multi-item orders). Likely cause: each seller ships separately, the order's delivery date reflects the first parcel, and the review survey arrives while part of the order is still missing (65% of these reviews have a written comment vs 41%). Worth confirming by reading the comments.
select case when n_sellers > 1 then '2+ sellers' else '1 seller' end as order_type,
       count(*)                                  as delivered_orders,
       round(100 * avg(is_late::int), 1)         as late_pct,
       round(100 * avg(is_bad_review::int), 1)   as bad_review_pct
from core.fct_orders
where is_delivered
group by 1
order by 1;
