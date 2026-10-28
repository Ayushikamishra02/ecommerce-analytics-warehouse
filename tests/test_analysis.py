"""The headline findings in the README are reproducible (tolerances allow for library-version noise)."""
import pytest

from olistwh import analysis


@pytest.fixture(scope="module")
def findings(con):
    return analysis.all_findings(con)


def test_growth(findings):
    g = findings["growth"]
    assert g["complete_months"] == 20
    assert g["gmv_growth_jan_aug"] == pytest.approx(1.404, abs=0.002)
    assert g["best_month"] == "2017-11-01"
    assert g["black_friday_2017_orders"] == 1166


def test_late_delivery_and_reviews(findings):
    lv = findings["late_vs_review"]
    assert lv["bad_review_rate_late"] == pytest.approx(0.629, abs=0.002)
    assert lv["bad_review_rate_on_time"] == pytest.approx(0.095, abs=0.002)
    lo, hi = lv["difference_ci"]
    assert lo < lv["difference"] < hi and lo > 0.5


def test_late_effect_survives_controls(findings):
    m = findings["late_model"]
    assert m["n"] == 96_469
    assert m["odds_ratio_late"] == pytest.approx(18.1, abs=0.3)
    assert m["ci"][0] > 15


def test_retention_is_low(findings):
    r = findings["retention"]
    assert r["repeat_customers"] == 2888
    assert r["repeat_rate"] == pytest.approx(0.0304, abs=0.0005)


def test_seller_concentration(findings):
    s = findings["sellers"]
    assert s["sellers"] == 3053
    assert s["sellers_for_80pct_gmv"] == 558
    assert s["of_which_avg_review_below_3_5"] == 39


def test_monthly_correlation_is_positive(findings):
    c = findings["monthly_correlation"]
    assert c["spearman_rho"] > 0.5 and c["p_value"] < 0.01
