-- Note: the public Olist sample only contains orders that received a review survey, so step 5 ~= step 4.
-- Order lifecycle "funnel": how many orders reach each stage, and how long each step takes (median hours).
with o as (select * from {{ ref('fct_orders') }})
select 1 as step, 'purchased' as stage, count(*) as orders, null::double as median_hours_from_previous from o
union all
select 2, 'approved', count(approved_at), median(date_diff('minute', purchased_at, approved_at) / 60.0) from o
union all
select 3, 'handed to carrier', count(shipped_at), median(date_diff('minute', approved_at, shipped_at) / 60.0) from o
union all
select 4, 'delivered', count(*) filter (where is_delivered),
       median(date_diff('minute', shipped_at, delivered_at) / 60.0) filter (where is_delivered) from o
union all
select 5, 'review answered', count(*) filter (where is_delivered and has_review),
       median(date_diff('minute', delivered_at, review_answered_at) / 60.0) filter (where is_delivered and has_review) from o
order by step
