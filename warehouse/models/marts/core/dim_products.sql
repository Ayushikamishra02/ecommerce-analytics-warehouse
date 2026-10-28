select product_id, category, category_missing, photos, weight_g, volume_cm3
from {{ ref('stg_products') }}
