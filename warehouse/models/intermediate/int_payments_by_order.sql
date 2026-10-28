-- Payments rolled up to one row per order; the main payment type is the one carrying the most value.
with ranked as (
    select *, row_number() over (partition by order_id order by payment_value desc, payment_sequential) as rn
    from {{ ref('stg_payments') }}
)
select
    order_id,
    sum(payment_value)                                  as payment_total,
    count(*)                                            as n_payments,
    max(payment_installments)                           as installments,
    max(case when rn = 1 then payment_type end)         as payment_type,
    bool_or(payment_type = 'voucher')                   as used_voucher
from ranked
group by order_id
