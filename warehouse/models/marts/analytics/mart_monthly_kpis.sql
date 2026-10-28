-- Monthly business KPIs. GMV = item prices + freight of valid sales (not canceled / unavailable).
with o as (select * from {{ ref('fct_orders') }} where is_valid_sale)
select
    purchase_month                                                    as month,
    count(*)                                                          as orders,
    count(distinct customer_key)                                      as customers,
    count(distinct customer_key) filter (where customer_order_number = 1) as new_customers,
    sum(order_value)                                                  as gmv,
    sum(items_value)                                                  as items_value,
    sum(freight_value)                                                as freight_value,
    sum(order_value) / count(*)                                       as avg_order_value,
    avg(n_items)                                                      as items_per_order,
    count(*) filter (where is_delivered)                              as delivered_orders,
    avg(case when is_delivered then is_late::int end)                 as late_rate,
    avg(case when is_delivered then delivery_days end)                as avg_delivery_days,
    avg(review_score)                                                 as avg_review_score,
    avg(is_bad_review::int)                                           as bad_review_rate,
    purchase_month between '{{ var("first_complete_month") }}' and '{{ var("last_complete_month") }}' as is_complete_month
from o
group by 1
order by 1
