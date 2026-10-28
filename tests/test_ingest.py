"""The raw layer is a faithful copy of the CSVs."""
import pytest

from olistwh.ingest import FILES, TEXT_COLUMNS

RAW_ROWS = {"customers": 99_441, "geolocation": 1_000_163, "order_items": 112_650, "order_payments": 103_886,
            "order_reviews": 100_000, "orders": 99_441, "products": 32_951, "sellers": 3_095,
            "category_translation": 71}


def test_every_file_has_a_checksum():
    assert set(FILES) == set(RAW_ROWS)
    assert all(len(sha) == 64 for _, sha in FILES.values())


@pytest.mark.parametrize("table,rows", RAW_ROWS.items())
def test_raw_row_counts(one, table, rows):
    assert one(f"select count(*) from raw.{table}") == rows


def test_zip_prefixes_keep_leading_zeros(con):
    types = dict(con.execute("select column_name, data_type from information_schema.columns "
                             "where table_schema = 'raw'").fetchall())
    for col in TEXT_COLUMNS:
        assert types[col] == "VARCHAR"
    assert con.execute("select count(*) from raw.customers where customer_zip_code_prefix like '0%'").fetchone()[0] > 0
