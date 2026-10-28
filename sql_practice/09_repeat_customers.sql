-- Level: medium
-- Question: What share of customers ordered more than once? (Careful: customer_id is per ORDER in Olist;
--           the real person is customer_unique_id, which the warehouse calls customer_key.)
-- Concepts: two-level aggregation, the "wrong id" trap
-- Takeaway: Only ~3% of customers ever return. Counting customer_id instead would report 0% repeat, because Olist issues a new customer_id for every order.
with per_customer as (
    select customer_key, count(*) as orders
    from core.fct_orders
    where is_valid_sale
    group by 1
)
select count(*)                                              as customers,
       count(*) filter (where orders >= 2)                   as repeat_customers,
       round(100.0 * count(*) filter (where orders >= 2) / count(*), 2) as repeat_pct,
       max(orders)                                           as max_orders_by_one_customer
from per_customer;
