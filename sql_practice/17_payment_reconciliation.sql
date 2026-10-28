-- Level: hard
-- Question: Reconcile payments against items + freight. How many valid orders differ by more than R$1, and what
--           is the typical gap? (Data-quality check that finance teams run.)
-- Concepts: aggregating two child tables separately BEFORE joining (joining first would multiply rows)
-- Takeaway: 0.25% of orders don't reconcile; the warehouse tracks this with a dbt test set to warn (not fail), because interest on installments and vouchers explain most gaps.
with items as (
    select order_id, sum(price + freight_value) as items_total
    from raw.order_items group by 1
), pays as (
    select order_id, sum(payment_value) as paid
    from raw.order_payments group by 1
)
select count(*)                                                    as orders_compared,
       count(*) filter (where abs(paid - items_total) > 1)         as mismatched,
       round(100.0 * count(*) filter (where abs(paid - items_total) > 1) / count(*), 2) as mismatched_pct,
       round(median(paid - items_total) filter (where abs(paid - items_total) > 1), 2)  as median_gap
from items join pays using (order_id)
join raw.orders o using (order_id)
where o.order_status not in ('canceled', 'unavailable');
