-- One row per order: the central fact table. Money in Brazilian reais (BRL).
with orders as (select * from {{ ref('stg_orders') }}),
customers as (select * from {{ ref('stg_customers') }}),
items as (select * from {{ ref('int_order_items_by_order') }}),
payments as (select * from {{ ref('int_payments_by_order') }}),
reviews as (select * from {{ ref('stg_reviews') }}),
distance as (select order_id, avg(distance_km) as avg_distance_km
             from {{ ref('int_item_distance') }} group by 1)
select
    o.order_id,
    c.customer_unique_id                                                as customer_key,
    o.customer_id,
    c.state                                                             as customer_state,
    r.region                                                            as customer_region,
    o.order_status,
    o.order_status not in ('canceled', 'unavailable')                   as is_valid_sale,
    o.order_status = 'delivered' and o.delivered_at is not null         as is_delivered,
    o.purchased_at,
    o.purchase_date,
    o.purchase_month,
    o.approved_at,
    o.shipped_at,
    o.delivered_at,
    o.estimated_delivery_at,
    -- money
    coalesce(i.items_value, 0)                                          as items_value,
    coalesce(i.freight_value, 0)                                        as freight_value,
    coalesce(i.items_value, 0) + coalesce(i.freight_value, 0)           as order_value,
    p.payment_total,
    p.payment_type,
    p.installments,
    p.used_voucher,
    i.n_items,
    i.n_sellers,
    i.main_category,
    d.avg_distance_km,
    -- delivery (days, fractional)
    date_diff('minute', o.purchased_at, o.delivered_at) / 1440.0        as delivery_days,
    date_diff('minute', o.purchased_at, o.estimated_delivery_at) / 1440.0 as promised_days,
    date_diff('day', cast(o.estimated_delivery_at as date), cast(o.delivered_at as date)) as days_late,
    cast(o.delivered_at as date) > cast(o.estimated_delivery_at as date) as is_late,
    -- review
    rv.review_score,
    rv.review_score is not null                                         as has_review,
    rv.review_score <= {{ var('bad_review_max_stars') }}               as is_bad_review,
    rv.has_comment                                                      as review_has_comment,
    rv.review_answered_at,
    -- customer sequence
    row_number() over (partition by c.customer_unique_id order by o.purchased_at, o.order_id) as customer_order_number
from orders o
join customers c using (customer_id)
left join {{ ref('state_regions') }} r on r.state = c.state
left join items i using (order_id)
left join payments p using (order_id)
left join reviews rv using (order_id)
left join distance d using (order_id)
