"""All dbt data tests (68 of them: keys, relationships, accepted values, reconciliations) must pass."""
import os
import shutil
import subprocess

import pytest

from olistwh.ingest import DB, ROOT


@pytest.mark.skipif(not DB.exists(), reason="warehouse not built")
@pytest.mark.skipif(shutil.which("dbt") is None, reason="dbt CLI not on PATH")
def test_dbt_data_tests_pass():
    env = {**os.environ, "OLIST_DB": str(DB), "DBT_PROFILES_DIR": str(ROOT / "warehouse")}
    r = subprocess.run(["dbt", "test", "--project-dir", str(ROOT / "warehouse")], env=env, capture_output=True,
                       text=True, timeout=600)
    assert r.returncode == 0, r.stdout[-3000:]
    assert "ERROR=0" in r.stdout and "FAIL=" not in r.stdout.replace("FAIL=0", "")
