-- Known data issue, tracked rather than hidden: some orders' payments differ from items + freight
-- (installment interest, vouchers). Warn if more than 0.5% of valid orders differ by over 1 BRL.
{{ config(severity='warn', warn_if='>0') }}
select count(*) as mismatched_orders
from {{ ref('fct_orders') }}
where is_valid_sale and payment_total is not null and abs(payment_total - order_value) > 1
having count(*) > 0.005 * (select count(*) from {{ ref('fct_orders') }} where is_valid_sale)
