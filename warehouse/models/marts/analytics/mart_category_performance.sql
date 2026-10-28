select
    category,
    count(distinct order_id)                             as orders,
    sum(item_value)                                      as gmv,
    avg(item_price)                                      as avg_price,
    sum(item_freight) / sum(item_value)                  as freight_share,
    avg(review_score)                                    as avg_review_score,
    avg(case when is_delivered then is_late::int end)    as late_rate
from {{ ref('fct_order_items') }}
where is_valid_sale
group by 1
