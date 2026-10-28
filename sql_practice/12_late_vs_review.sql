-- Level: easy
-- Question: Compare average review score and the share of 1-2 star reviews for late vs on-time orders.
-- Concepts: CASE for readable labels, conditional aggregates
-- Takeaway: A late order is ~6.6x more likely to get 1-2 stars. Lesson 04 checks this holds after controlling for region, basket and category (logistic regression).
select case when is_late then 'late' else 'on time' end   as delivery,
       count(*)                                           as orders,
       round(avg(review_score), 2)                        as avg_review,
       round(100 * avg(is_bad_review::int), 1)            as bad_review_pct
from core.fct_orders
where is_delivered and has_review
group by 1
order by 1;
