-- Seller scorecard and Pareto ranking by GMV (valid sales).
with s as (
    select
        seller_id,
        any_value(seller_state)                         as seller_state,
        count(distinct order_id)                        as orders,
        count(*)                                        as items,
        sum(item_value)                                 as gmv,
        avg(review_score)                               as avg_review_score,
        avg(case when is_delivered then is_late::int end) as late_rate
    from {{ ref('fct_order_items') }}
    where is_valid_sale
    group by 1
)
select *,
    row_number() over (order by gmv desc)                                   as gmv_rank,
    gmv / sum(gmv) over ()                                                  as gmv_share,
    sum(gmv) over (order by gmv desc rows unbounded preceding) / sum(gmv) over () as cumulative_gmv_share
from s
