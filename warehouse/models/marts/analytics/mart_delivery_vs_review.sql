-- Dose-response: review scores by how early/late the order arrived relative to the promised date.
with o as (
    select *,
        case
            when days_late <= -10 then '10+ days early'
            when days_late <= -5  then '5-9 days early'
            when days_late <= 0   then '0-4 days early'
            when days_late <= 3   then '1-3 days late'
            when days_late <= 7   then '4-7 days late'
            when days_late <= 14  then '8-14 days late'
            else '15+ days late'
        end as lateness
    from {{ ref('fct_orders') }}
    where is_delivered and has_review
)
select
    lateness,
    min(days_late)            as sort_key,
    count(*)                  as orders,
    avg(review_score)         as avg_review_score,
    avg(is_bad_review::int)   as bad_review_rate,
    avg((review_score = 5)::int) as five_star_rate
from o
group by 1
order by sort_key
