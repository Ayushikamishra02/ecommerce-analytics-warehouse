-- Item-level facts rolled up to one row per order.
with items as (
    select i.*, p.category
    from {{ ref('stg_order_items') }} i
    left join {{ ref('stg_products') }} p using (product_id)
),
main_category as (   -- the category of the order's most expensive item
    select order_id, category as main_category
    from (select order_id, category,
                 row_number() over (partition by order_id order by item_price desc, product_id) as rn
          from items)
    where rn = 1
)
select
    order_id,
    count(*)                    as n_items,
    count(distinct product_id)  as n_products,
    count(distinct seller_id)   as n_sellers,
    sum(item_price)             as items_value,
    sum(item_freight)           as freight_value,
    any_value(m.main_category)  as main_category
from items
left join main_category m using (order_id)
group by order_id
