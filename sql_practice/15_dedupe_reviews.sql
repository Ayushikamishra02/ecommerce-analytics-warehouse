-- Level: medium
-- Question: Some orders have several reviews in the raw data. Keep only the most recently answered review per
--           order and show how many rows that removes.
-- Concepts: deduplication with ROW_NUMBER, the most common data-cleaning pattern in SQL interviews
with ranked as (
    select *,
           row_number() over (partition by order_id
                              order by review_answer_timestamp desc, review_creation_date desc, review_id) as rn
    from raw.order_reviews
)
select count(*)                          as raw_rows,
       count(*) filter (where rn = 1)    as deduped_rows,
       count(*) filter (where rn > 1)    as removed,
       count(distinct order_id)          as distinct_orders
from ranked;
