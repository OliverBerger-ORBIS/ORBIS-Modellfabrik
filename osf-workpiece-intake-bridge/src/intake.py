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
    Return intake payload when RGB_NFC finishes with NFC id and known color.

    Output keys: productRaw, nfc, timestamp. orderId is not part of the contract
    (at intake time APS still has \"0\"; real order UUID arrives later via FTS/CCU).
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
        workpiece = metadata.get("workpiece")
        if isinstance(workpiece, dict) and workpiece.get("type"):
            product_raw = workpiece.get("type")
    if product_raw is None or product_raw == "":
        # Fallback: some APS variants put color on loads[]
        loads = payload.get("loads")
        if isinstance(loads, list) and loads:
            first = loads[0]
            if isinstance(first, dict) and first.get("type"):
                product_raw = first.get("type")
    # Wait for a later RGB_NFC FINISHED that carries color — do not publish UNKNOWN.
    # APS often emits NFC first (~1s), then the same NFC with metadata.type.
    if product_raw is None or product_raw == "":
        return None
    product_raw = str(product_raw).upper()
    if product_raw in ("UNKNOWN", "NONE", "NULL"):
        return None

    ts = action.get("timestamp") or payload.get("timestamp") or now_iso
    if not ts:
        return None

    return {
        "productRaw": product_raw,
        "nfc": nfc_str,
        "timestamp": str(ts),
    }
