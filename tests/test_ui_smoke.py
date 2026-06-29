"""Headless smoke test for the Streamlit UI using Streamlit's AppTest harness.

Skipped automatically when the optional ``ui`` extra (streamlit) isn't installed,
so the core test run stays dependency-free.
"""

from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

APP = str(Path(__file__).resolve().parent.parent / "ui" / "app.py")


def test_app_runs_without_exception():
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception
    # Title rendered.
    assert any("Agent Eval Engine" in t.value for t in at.title)
    # Reference paths and candidate sections rendered some subheaders.
    assert len(at.subheader) >= 2


def test_clicking_score_button_produces_a_score():
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert at.button, "expected a Score button"
    at.button[0].click().run()
    assert not at.exception
    # After scoring, three metrics appear (Score / Best match / Comparator).
    assert len(at.metric) >= 3
    score_metric = next(m for m in at.metric if m.label == "Score")
    value = float(score_metric.value)
    assert 0.0 <= value <= 1.0
