-- One row per PERSON (customer_unique_id), with lifetime facts over valid sales.
with o as (select * from {{ ref('fct_orders') }}),
latest as (
    select customer_key, customer_state, customer_region
    from (select *, row_number() over (partition by customer_key order by purchased_at desc) as rn from o)
    where rn = 1
),
c as (
    select distinct on (cu.customer_unique_id) cu.customer_unique_id as customer_key, cu.city, cu.zip_prefix
    from {{ ref('stg_customers') }} cu
    join {{ ref('stg_orders') }} so using (customer_id)
    order by cu.customer_unique_id, so.purchased_at desc
)
select
    l.customer_key,
    c.city,
    c.zip_prefix,
    l.customer_state                                         as state,
    l.customer_region                                        as region,
    min(o.purchased_at)                                      as first_order_at,
    max(o.purchased_at)                                      as last_order_at,
    date_trunc('month', min(o.purchased_at))::date           as cohort_month,
    count(*)                                                 as orders,
    count(*) filter (where o.is_valid_sale)                  as valid_orders,
    coalesce(sum(o.order_value) filter (where o.is_valid_sale), 0) as lifetime_value,
    avg(o.review_score)                                      as avg_review_score
from o
join latest l using (customer_key)
join c using (customer_key)
group by all
