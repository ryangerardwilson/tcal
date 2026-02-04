import json
from datetime import datetime

import pytest

from models import Event, JTBD, NorthStarMetrics
from orchestrator import _parse_row_editor_json, _row_editor_seed


def _sample_event() -> Event:
    return Event(
        bucket="personal_development",
        jtbd=JTBD(
            x=datetime(2026, 2, 20, 14, 30, 0),
            y="draft community update",
            z="clarify roadmap",
        ),
        nsm=NorthStarMetrics(p=7.0, q=4.5, r=6.0),
    )


def test_row_editor_roundtrip_preserves_fields() -> None:
    event = _sample_event()
    payload = _row_editor_seed(event)
    raw = json.dumps(payload, indent=2)

    parsed_event = _parse_row_editor_json(raw, event.bucket)

    assert parsed_event.bucket == event.bucket
    assert parsed_event.jtbd.x == event.jtbd.x
    assert parsed_event.jtbd.y == event.jtbd.y
    assert parsed_event.jtbd.z == event.jtbd.z
    assert parsed_event.nsm.p == pytest.approx(event.nsm.p)
    assert parsed_event.nsm.q == pytest.approx(event.nsm.q)
    assert parsed_event.nsm.r == pytest.approx(event.nsm.r)


def test_row_editor_respects_bucket_override() -> None:
    event = _sample_event()
    payload = _row_editor_seed(event)
    payload["bucket"] = "economic"
    raw = json.dumps(payload, indent=2)

    parsed_event = _parse_row_editor_json(raw, event.bucket)

    assert parsed_event.bucket == "economic"


def test_row_editor_requires_jtbd_and_nsm() -> None:
    event = _sample_event()
    payload = _row_editor_seed(event)
    incomplete_payload = {"nsm": payload["nsm"]}
    raw = json.dumps(incomplete_payload, indent=2)

    with pytest.raises(ValueError):
        _parse_row_editor_json(raw, event.bucket)
