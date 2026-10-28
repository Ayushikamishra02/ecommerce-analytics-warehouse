"""Shared fixtures. Most tests need the built warehouse: run `olist build` first (CI does)."""
import pytest

from olistwh.ingest import DB


def pytest_collection_modifyitems(config, items):
    # dbt opens the database read-write, so its test file must run before any read-only connection exists.
    items.sort(key=lambda i: 0 if "test_00_dbt" in str(i.fspath) else 1)


@pytest.fixture(scope="session")
def con():
    if not DB.exists():
        pytest.skip("warehouse not built: run `olist build`")
    import duckdb

    c = duckdb.connect(str(DB), read_only=True)
    yield c
    c.close()


@pytest.fixture(scope="session")
def one(con):
    return lambda sql: con.execute(sql).fetchone()[0]
