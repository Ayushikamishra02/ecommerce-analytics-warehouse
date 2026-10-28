-- An order can't arrive before it was bought.
select order_id from {{ ref('fct_orders') }} where delivered_at < purchased_at
