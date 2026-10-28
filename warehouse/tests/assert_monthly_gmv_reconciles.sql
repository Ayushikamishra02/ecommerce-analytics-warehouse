-- The monthly KPI table must add up to the order fact table (to the cent).
select 1
from (select sum(gmv) as kpi from {{ ref('mart_monthly_kpis') }}) k,
     (select sum(order_value) as fact from {{ ref('fct_orders') }} where is_valid_sale) f
where abs(k.kpi - f.fact) > 0.01
