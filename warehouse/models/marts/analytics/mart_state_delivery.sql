-- Delivery experience by customer state (delivered orders).
select
    o.customer_state                       as state,
    any_value(o.customer_region)           as region,
    count(*)                               as delivered_orders,
    avg(o.delivery_days)                   as avg_delivery_days,
    median(o.delivery_days)                as median_delivery_days,
    avg(o.promised_days)                   as avg_promised_days,
    avg(o.is_late::int)                    as late_rate,
    sum(o.freight_value) / sum(o.order_value) as freight_share,
    avg(o.review_score)                    as avg_review_score,
    avg(o.avg_distance_km)                 as avg_distance_km
from {{ ref('fct_orders') }} o
where o.is_delivered
group by 1
