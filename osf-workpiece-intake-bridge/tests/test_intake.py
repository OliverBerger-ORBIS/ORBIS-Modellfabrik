from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(ROOT))

from intake import build_intake_event  # noqa: E402


def test_rgb_nfc_finished_builds_event() -> None:
    payload = {
        "orderId": "0",
        "actionState": {
            "command": "RGB_NFC",
            "state": "FINISHED",
            "result": "92e0ad91595f63",
            "metadata": {"type": "WHITE"},
            "timestamp": "2026-08-07T09:11:46.905Z",
        },
    }
    event = build_intake_event(payload)
    assert event == {
        "productRaw": "WHITE",
        "nfc": "92e0ad91595f63",
        "timestamp": "2026-08-07T09:11:46.905Z",
    }
    assert "orderId" not in event


def test_order_id_never_included_even_when_aps_has_uuid() -> None:
    """Intake is color+NFC only; storage/production orderId arrives later via APS."""
    payload = {
        "orderId": "1bb6b56d-661b-43a0-a14a-866fa737d352",
        "actionState": {
            "command": "RGB_NFC",
            "state": "FINISHED",
            "result": "abc",
            "metadata": {"type": "RED"},
            "timestamp": "2026-08-07T09:11:46.905Z",
        },
    }
    event = build_intake_event(payload)
    assert event == {
        "productRaw": "RED",
        "nfc": "abc",
        "timestamp": "2026-08-07T09:11:46.905Z",
    }
    assert "orderId" not in event


def test_ignores_running_and_missing_result() -> None:
    assert (
        build_intake_event(
            {
                "actionState": {
                    "command": "RGB_NFC",
                    "state": "RUNNING",
                    "metadata": {"type": "BLUE"},
                }
            }
        )
        is None
    )
    assert (
        build_intake_event(
            {
                "actionState": {
                    "command": "RGB_NFC",
                    "state": "FINISHED",
                    "result": None,
                    "metadata": {"type": "BLUE"},
                }
            }
        )
        is None
    )


def test_ignores_other_commands() -> None:
    assert (
        build_intake_event(
            {
                "actionState": {
                    "command": "INPUT_RGB",
                    "state": "FINISHED",
                    "result": "x",
                }
            }
        )
        is None
    )


def test_waits_when_color_missing() -> None:
    """First APS RGB_NFC often has NFC but no type — do not publish UNKNOWN."""
    assert (
        build_intake_event(
            {
                "orderId": "0",
                "actionState": {
                    "command": "RGB_NFC",
                    "state": "FINISHED",
                    "result": "93b29ba34a2334",
                    "timestamp": "2026-08-25T06:31:57.911Z",
                },
            }
        )
        is None
    )


def test_publishes_when_color_arrives_on_later_rgb_nfc() -> None:
    event = build_intake_event(
        {
            "orderId": "0",
            "actionState": {
                "command": "RGB_NFC",
                "state": "FINISHED",
                "result": "93b29ba34a2334",
                "metadata": {"type": "BLUE"},
                "timestamp": "2026-08-25T06:31:58.000Z",
            },
        }
    )
    assert event == {
        "productRaw": "BLUE",
        "nfc": "93b29ba34a2334",
        "timestamp": "2026-08-25T06:31:58.000Z",
    }


def test_color_from_metadata_workpiece_type() -> None:
    event = build_intake_event(
        {
            "actionState": {
                "command": "RGB_NFC",
                "state": "FINISHED",
                "result": "nfc-1",
                "metadata": {"workpiece": {"type": "WHITE", "workpieceId": "nfc-1"}},
                "timestamp": "2026-08-25T06:31:58.000Z",
            },
        }
    )
    assert event is not None
    assert event["productRaw"] == "WHITE"


def test_rejects_explicit_unknown_type() -> None:
    assert (
        build_intake_event(
            {
                "actionState": {
                    "command": "RGB_NFC",
                    "state": "FINISHED",
                    "result": "nfc-2",
                    "metadata": {"type": "UNKNOWN"},
                    "timestamp": "2026-08-25T06:31:58.000Z",
                },
            }
        )
        is None
    )
