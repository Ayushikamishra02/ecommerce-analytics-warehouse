-- Monthly acquisition cohorts: of the customers whose FIRST order was in month M, what share ordered again
-- k months later? (Valid sales only; month 0 is always 100%.)
with o as (
    select customer_key, purchase_month
    from {{ ref('fct_orders') }}
    where is_valid_sale
),
first_month as (
    select customer_key, min(purchase_month) as cohort_month from o group by 1
),
activity as (
    select distinct f.cohort_month, o.customer_key,
           date_diff('month', f.cohort_month, o.purchase_month) as months_since
    from o join first_month f using (customer_key)
),
sizes as (select cohort_month, count(*) as cohort_size from first_month group by 1)
select
    a.cohort_month,
    a.months_since,
    s.cohort_size,
    count(*)                         as active_customers,
    count(*) / s.cohort_size         as retention_rate
from activity a
join sizes s using (cohort_month)
group by a.cohort_month, a.months_since, s.cohort_size
order by 1, 2
