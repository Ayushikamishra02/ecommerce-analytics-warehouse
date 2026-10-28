-- The raw file has 827 repeated review_ids and 559 orders with more than one review.
-- Keep ONE review per order: the most recently answered one.
with ranked as (
    select
        review_id,
        order_id,
        review_score,
        review_comment_title,
        review_comment_message,
        review_creation_date     as review_created_at,
        review_answer_timestamp  as review_answered_at,
        row_number() over (partition by order_id
                           order by review_answer_timestamp desc, review_id) as rn
    from {{ source('raw', 'order_reviews') }}
)
select
    review_id,
    order_id,
    review_score,
    review_comment_title,
    review_comment_message,
    review_comment_message is not null as has_comment,
    review_created_at,
    review_answered_at
from ranked
where rn = 1
