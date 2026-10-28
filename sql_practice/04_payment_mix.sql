-- Level: easy
-- Question: For each payment type: orders, average order value, and average number of installments.
-- Concepts: GROUP BY, AVG, NULL handling (one order has no payment record)
select coalesce(payment_type, '(no payment)')   as payment_type,
       count(*)                                  as orders,
       round(avg(order_value), 2)                as avg_order_value,
       round(avg(installments), 2)               as avg_installments
from core.fct_orders
where is_valid_sale
group by 1
order by orders desc;
