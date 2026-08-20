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


def test_order_id_included_when_meaningful() -> None:
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
    assert event is not None
    assert event["orderId"] == "1bb6b56d-661b-43a0-a14a-866fa737d352"


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
