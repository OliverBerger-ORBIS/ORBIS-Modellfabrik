"""Parse APS DPS module state → ORBIS workpiece intake event."""

from __future__ import annotations

from typing import Any


def _action_state(payload: dict[str, Any]) -> dict[str, Any] | None:
    action = payload.get("actionState")
    if isinstance(action, dict):
        return action
    return None


def build_intake_event(payload: dict[str, Any], *, now_iso: str | None = None) -> dict[str, Any] | None:
    """
    Return intake payload when RGB_NFC finishes with an NFC id; otherwise None.

    Output keys: productRaw, nfc, timestamp; orderId only if present and not \"0\".
    """
    action = _action_state(payload)
    if not action:
        return None
    if action.get("command") != "RGB_NFC":
        return None
    if str(action.get("state", "")).upper() != "FINISHED":
        return None

    nfc = action.get("result")
    if nfc is None or nfc == "":
        return None
    nfc_str = str(nfc).strip()
    if not nfc_str:
        return None

    metadata = action.get("metadata") if isinstance(action.get("metadata"), dict) else {}
    product_raw = metadata.get("type")
    if product_raw is None or product_raw == "":
        # Fallback: some APS variants put color on loads[]
        loads = payload.get("loads")
        if isinstance(loads, list) and loads:
            first = loads[0]
            if isinstance(first, dict) and first.get("type"):
                product_raw = first.get("type")
    if product_raw is None or product_raw == "":
        product_raw = "UNKNOWN"
    else:
        product_raw = str(product_raw).upper()

    ts = action.get("timestamp") or payload.get("timestamp") or now_iso
    if not ts:
        return None

    event: dict[str, Any] = {
        "productRaw": product_raw,
        "nfc": nfc_str,
        "timestamp": str(ts),
    }

    order_id = payload.get("orderId")
    if order_id is not None and str(order_id) not in ("", "0"):
        event["orderId"] = str(order_id)

    return event
