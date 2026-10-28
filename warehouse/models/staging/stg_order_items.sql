-- One row per item in an order (an order with 3 of the same product has 3 rows).
select
    order_id,
    order_item_id,
    product_id,
    seller_id,
    shipping_limit_date  as shipping_limit_at,
    price                as item_price,
    freight_value        as item_freight
from {{ source('raw', 'order_items') }}
