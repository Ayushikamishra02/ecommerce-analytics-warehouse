select
    s.seller_id,
    s.city,
    s.state,
    r.region,
    g.lat,
    g.lng
from {{ ref('stg_sellers') }} s
left join {{ ref('state_regions') }} r on r.state = s.state
left join {{ ref('stg_geolocation') }} g on g.zip_prefix = s.zip_prefix
