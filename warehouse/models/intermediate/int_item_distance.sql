-- Straight-line (haversine) distance between seller and customer for each order item, in km.
with o as (
    select o.order_id, c.zip_prefix as customer_zip
    from {{ ref('stg_orders') }} o
    join {{ ref('stg_customers') }} c using (customer_id)
)
select
    i.order_id,
    i.order_item_id,
    2 * 6371 * asin(sqrt(
        pow(sin(radians(gc.lat - gs.lat) / 2), 2)
        + cos(radians(gs.lat)) * cos(radians(gc.lat)) * pow(sin(radians(gc.lng - gs.lng) / 2), 2)
    )) as distance_km
from {{ ref('stg_order_items') }} i
join o using (order_id)
join {{ ref('stg_sellers') }} s using (seller_id)
left join {{ ref('stg_geolocation') }} gs on gs.zip_prefix = s.zip_prefix
left join {{ ref('stg_geolocation') }} gc on gc.zip_prefix = o.customer_zip
