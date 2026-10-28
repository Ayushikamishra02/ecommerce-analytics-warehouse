-- Category names translated to English. 610 products have no category; 2 categories have no translation.
select
    p.product_id,
    coalesce(t.product_category_name_english, p.product_category_name, 'unknown') as category,
    p.product_category_name is null                                               as category_missing,
    p.product_photos_qty                                                          as photos,
    p.product_weight_g                                                            as weight_g,
    p.product_length_cm * p.product_height_cm * p.product_width_cm               as volume_cm3
from {{ source('raw', 'products') }} p
left join {{ source('raw', 'category_translation') }} t using (product_category_name)
