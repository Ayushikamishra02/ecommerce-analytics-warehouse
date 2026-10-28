-- 1,000,163 raw rows, many per zip prefix, some far outside Brazil (bad geocodes).
-- One row per zip prefix: the median of the points that fall inside Brazil's bounding box.
select
    geolocation_zip_code_prefix   as zip_prefix,
    median(geolocation_lat)       as lat,
    median(geolocation_lng)       as lng,
    count(*)                      as raw_points
from {{ source('raw', 'geolocation') }}
where geolocation_lat between -33.8 and 5.3
  and geolocation_lng between -73.99 and -34.79
group by 1
