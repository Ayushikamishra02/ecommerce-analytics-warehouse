-- One row per order item: the grain for seller, product and category analysis.
select
    i.order_id,
    i.order_item_id,
    i.product_id,
    i.seller_id,
    o.customer_key,
    o.purchase_date,
    o.purchase_month,
    o.order_status,
    o.is_valid_sale,
    o.is_delivered,
    o.is_late,
    o.review_score,
    p.category,
    s.state                    as seller_state,
    o.customer_state,
    i.item_price,
    i.item_freight,
    i.item_price + i.item_freight as item_value,
    d.distance_km
from {{ ref('stg_order_items') }} i
join {{ ref('fct_orders') }} o using (order_id)
left join {{ ref('stg_products') }} p using (product_id)
left join {{ ref('stg_sellers') }} s using (seller_id)
left join {{ ref('int_item_distance') }} d using (order_id, order_item_id)
