-- Olist issues a new customer_id for every order; customer_unique_id identifies the PERSON.
-- Any customer analysis (retention, repeat rate, RFM) must use customer_unique_id.
select
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix   as zip_prefix,
    customer_city              as city,
    customer_state             as state
from {{ source('raw', 'customers') }}
