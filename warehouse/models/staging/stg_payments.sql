-- One row per payment; an order can be paid with several (e.g. a voucher plus a credit card).
select
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    payment_value
from {{ source('raw', 'order_payments') }}
