"""Every SQL practice question parses, runs, and the key answers match the lesson."""
import pytest

from olistwh.sqlpractice import questions, run

QS = questions()


def test_question_headers():
    assert len(QS) == 22
    for q in QS:
        assert q["level"] in {"easy", "medium", "hard"}, q["file"]
        assert q["question"] and q["concepts"], q["file"]
        assert not q["sql"].lstrip().startswith("-- Question"), q["file"]


@pytest.mark.parametrize("q", QS, ids=[q["file"] for q in QS])
def test_query_runs(con, q):
    assert len(run(q, con)) > 0


def _answer(con, qid):
    return run(next(q for q in QS if q["id"] == qid), con)


def test_known_answers(con):
    assert _answer(con, "09").repeat_customers.iloc[0] == 2888
    assert _answer(con, "15").removed.iloc[0] == 559
    late = _answer(con, "12").set_index("delivery")
    assert late.loc["late", "bad_review_pct"] == pytest.approx(62.9, abs=0.1)
    assert _answer(con, "01").shape[0] == 20
    assert _answer(con, "02").category.iloc[0] == "health_beauty"
