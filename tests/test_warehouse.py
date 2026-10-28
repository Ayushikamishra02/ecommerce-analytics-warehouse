"""The cleaning rules and the star schema behave as documented."""


def test_one_review_per_order(one):
    assert one("select count(*) from staging.stg_reviews") == one("select count(distinct order_id) from raw.order_reviews")
    assert one("select count(*) - count(distinct order_id) from staging.stg_reviews") == 0


def test_customer_key_is_the_person_not_the_order(one):
    assert one("select count(*) from core.dim_customers") == 96_096
    assert one("select count(distinct customer_key) from core.fct_orders") == 96_096


def test_fact_grain(one):
    assert one("select count(*) from core.fct_orders") == 99_441
    assert one("select count(*) from core.fct_order_items") == 112_650


def test_item_fact_reconciles_to_order_fact(one):
    diff = one("""select abs((select sum(item_price + item_freight) from core.fct_order_items)
                           - (select sum(items_value + freight_value) from core.fct_orders))""")
    assert diff < 0.01


def test_monthly_mart_reconciles_to_fact(one):
    diff = one("""select abs((select sum(gmv) from analytics.mart_monthly_kpis)
                           - (select sum(order_value) from core.fct_orders where is_valid_sale))""")
    assert diff < 0.01


def test_valid_sales_exclude_canceled_and_unavailable(one):
    assert one("select count(*) from core.fct_orders where is_valid_sale "
               "and order_status in ('canceled', 'unavailable')") == 0
    assert one("select count(*) from core.fct_orders where is_valid_sale") == 98_207


def test_geolocation_is_one_point_per_zip_inside_brazil(one):
    assert one("select count(*) - count(distinct zip_prefix) from staging.stg_geolocation") == 0
    assert one("select count(*) from staging.stg_geolocation where lat not between -33.8 and 5.3 "
               "or lng not between -73.99 and -34.79") == 0


def test_every_product_has_a_category(one):
    assert one("select count(*) from core.dim_products where category is null") == 0
    assert one("select count(*) from core.dim_products where category = 'unknown'") == 610


def test_lateness_definition(one):
    # late means delivered on a later calendar day than promised
    assert one("select count(*) from core.fct_orders where is_late and days_late <= 0") == 0
    assert one("select count(*) from core.fct_orders where is_delivered and not is_late and days_late > 0") == 0


def test_cohort_month_zero_is_everyone(one):
    assert one("select count(*) from analytics.mart_cohort_retention where months_since = 0 "
               "and active_customers <> cohort_size") == 0


def test_rfm_covers_every_buyer(one):
    assert one("select count(*) from analytics.mart_rfm") == 94_990
    assert one("select count(distinct segment) from analytics.mart_rfm") == 7
