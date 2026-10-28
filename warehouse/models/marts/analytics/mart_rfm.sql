-- RFM segmentation (Recency, Frequency, Monetary) of every customer with a valid sale.
-- 97% of customers order once, so Frequency is "1 order" vs "2+ orders" rather than quintiles.
with c as (
    select
        customer_key,
        date_diff('day', max(purchased_at), (select max(purchased_at) from {{ ref('fct_orders') }}) ) as recency_days,
        count(*)            as frequency,
        sum(order_value)    as monetary
    from {{ ref('fct_orders') }}
    where is_valid_sale
    group by 1
),
scored as (
    select *,
        6 - ntile(5) over (order by recency_days)   as r_score,     -- 5 = most recent
        ntile(5) over (order by monetary)           as m_score,     -- 5 = highest spend
        case when frequency >= 2 then 2 else 1 end  as f_score
    from c
)
select *,
    case
        when f_score = 2 and r_score >= 4                 then 'Champions'
        when f_score = 2                                   then 'Loyal, lapsing'
        when r_score >= 4 and m_score >= 4                 then 'New big spenders'
        when r_score >= 4                                  then 'New customers'
        when r_score = 3                                   then 'Cooling'
        when m_score >= 4                                  then 'At risk, high value'
        else 'Hibernating'
    end as segment
from scored
