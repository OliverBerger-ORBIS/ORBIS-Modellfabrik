#!/usr/bin/env python3
"""
Utility script to extract compact MQTT fixture logs for the OMF3 dashboard.

The script reads one or more recorded session logs (JSON lines), filters for
topics relevant to the UI, and writes trimmed fixture files under
`omf3/testing/fixtures/orders/{...}`.

By default the script builds the predefined fixtures (white, blue, red, mixed)
that combine order, module and optional FTS telemetry for deterministic replay.

Usage examples:

    # Build all predefined fixtures
    python scripts/build_order_fixtures.py

    # Re-build only the white fixture
    python scripts/build_order_fixtures.py --only white

    # Dry-run to inspect which messages would be written
    python scripts/build_order_fixtures.py --only white --dry-run
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, List, Sequence, Set


REPO_ROOT = Path(__file__).resolve().parents[1]


def topic_matches(topic: str, patterns: Sequence[str]) -> bool:
    """Return True if the topic matches one of the supported patterns."""
    for pattern in patterns:
        if pattern.endswith("*"):
            if topic.startswith(pattern[:-1]):
                return True
        elif topic == pattern:
            return True
    return False


def extract_order_ids(payload: object) -> Set[str]:
    """Collect order ids from a decoded payload."""
    collected: Set[str] = set()

    if isinstance(payload, dict):
        order_id = payload.get("orderId")
        if isinstance(order_id, str) and order_id:
            collected.add(order_id)
    elif isinstance(payload, list):
        for entry in payload:
            if isinstance(entry, dict):
                order_id = entry.get("orderId")
                if isinstance(order_id, str) and order_id:
                    collected.add(order_id)
    return collected


def decode_payload(raw_payload: object) -> object:
    """Parse payload JSON strings into Python objects when possible."""
    if isinstance(raw_payload, str):
        try:
            return json.loads(raw_payload)
        except json.JSONDecodeError:
            return raw_payload
    return raw_payload


def iter_messages(paths: Sequence[Path]) -> Iterator[dict]:
    """Yield parsed JSON messages from all source paths."""
    for path in paths:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as exc:
                    raise RuntimeError(f"Failed to parse line in {path}: {exc}") from exc


def normalize_message(message: dict, decoded_payload: object) -> List[dict]:
    """
    Normalize a single MQTT message into one or multiple JSON objects.

    - Split order arrays (ccu/order/active/completed) into individual messages.
    - Ensure payloads are JSON strings for dict/list payloads.
    """

    topic = message.get("topic", "")
    base = {key: value for key, value in message.items() if key != "payload"}

    def encode_payload(payload_obj: object) -> object:
        if isinstance(payload_obj, (dict, list)):
            return json.dumps(payload_obj, ensure_ascii=False)
        return payload_obj

    if topic in {"ccu/order/active", "ccu/order/completed"} and isinstance(decoded_payload, list):
        normalized: List[dict] = []
        for entry in decoded_payload:
            normalized.append({**base, "payload": encode_payload(entry)})
        return normalized

    return [{**base, "payload": encode_payload(decoded_payload)}]


@dataclass
class FixtureConfig:
    name: str
    sources: List[Path]
    output: Path
    topic_patterns: List[str]
    order_ids: Set[str] = field(default_factory=set)
    passthrough_patterns: List[str] = field(default_factory=list)

    def resolve_sources(self) -> List[Path]:
        return [source if source.is_absolute() else REPO_ROOT / source for source in self.sources]

    def resolve_output(self) -> Path:
        return self.output if self.output.is_absolute() else REPO_ROOT / self.output


def build_fixture(config: FixtureConfig, dry_run: bool = False) -> int:
    """Create a trimmed fixture file according to the config."""
    resolved_sources = config.resolve_sources()
    output_path = config.resolve_output()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    retained: List[str] = []

    for message in iter_messages(resolved_sources):
        topic = message.get("topic", "")
        if not topic_matches(topic, config.topic_patterns):
            continue

        payload = decode_payload(message.get("payload"))
        order_ids = extract_order_ids(payload)

        keep = True
        if config.order_ids:
            keep = bool(order_ids & config.order_ids)
            if not keep and topic_matches(topic, config.passthrough_patterns):
                keep = True

        if not keep:
            continue

        for normalized in normalize_message(message, payload):
            if config.order_ids:
                normalized_payload = decode_payload(normalized.get("payload"))
                if not (extract_order_ids(normalized_payload) & config.order_ids):
                    continue
            retained.append(json.dumps(normalized, ensure_ascii=False))

    if dry_run:
        print(f"[DRY-RUN] {config.name}: would write {len(retained)} messages to {output_path}")
        return len(retained)

    with output_path.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(retained))
        handle.write("\n")

    print(f"[OK] {config.name}: wrote {len(retained)} messages to {output_path}")
    return len(retained)


def load_default_configs() -> List[FixtureConfig]:
    """Return fixture configurations for standard order demos."""
    return [
        FixtureConfig(
            name="white",
            sources=[
                Path("data/omf-data/sessions/production_order_white_20251110_184459.log"),
            ],
            output=Path("omf3/testing/fixtures/orders/white/orders.log"),
            topic_patterns=[
                "ccu/order/active",
                "ccu/order/completed",
                "module/v1/ff/*",
                "warehouse/stock",
                "warehouse/stock/*",
                "fts/v1/ff/*",
            ],
            order_ids={"bc51e53d-413a-4cd7-b128-b4407fba3c23"},
            passthrough_patterns=["warehouse/stock"],
        ),
        FixtureConfig(
            name="blue",
            sources=[
                Path("data/omf-data/sessions/production_order_blue_20251110_180619.log"),
            ],
            output=Path("omf3/testing/fixtures/orders/blue/orders.log"),
            topic_patterns=[
                "ccu/order/active",
                "ccu/order/completed",
                "module/v1/ff/*",
                "warehouse/stock",
                "warehouse/stock/*",
                "fts/v1/ff/*",
            ],
            order_ids={"ceca8bef-bbe8-4012-aa18-725d7af68a10"},
            passthrough_patterns=["warehouse/stock"],
        ),
        FixtureConfig(
            name="red",
            sources=[
                Path("data/omf-data/sessions/production_order_red_20251110_180152.log"),
            ],
            output=Path("omf3/testing/fixtures/orders/red/orders.log"),
            topic_patterns=[
                "ccu/order/active",
                "ccu/order/completed",
                "module/v1/ff/*",
                "warehouse/stock",
                "warehouse/stock/*",
                "fts/v1/ff/*",
            ],
            order_ids={"c9da720e-98e6-4d96-84d3-7baad5c5383d"},
            passthrough_patterns=["warehouse/stock"],
        ),
        FixtureConfig(
            name="mixed",
            sources=[
                Path("data/omf-data/sessions/production_order_bwr_20251110_182819.log"),
            ],
            output=Path("omf3/testing/fixtures/orders/mixed/orders.log"),
            topic_patterns=[
                "ccu/order/active",
                "ccu/order/completed",
                "module/v1/ff/*",
                "warehouse/stock",
                "warehouse/stock/*",
                "fts/v1/ff/*",
            ],
            order_ids={
                "8e79e45c-f4dc-4e2a-b7b9-8f56c3238c52",
                "2ada017e-dc9e-4f63-9c08-64e7c59f20ff",
                "8fd237e5-2170-4570-8023-36e8b4cd9b30",
                "dc7b8963-68b6-4b8b-9c94-c271d11b64dc",
            },
            passthrough_patterns=["warehouse/stock"],
        ),
        FixtureConfig(
            name="storage",
            sources=[
                Path("data/omf-data/sessions/storage_order_white_20251110_181619.log"),
            ],
            output=Path("omf3/testing/fixtures/orders/storage/orders.log"),
            topic_patterns=[
                "ccu/order/active",
                "ccu/order/completed",
                "module/v1/ff/*",
                "warehouse/stock",
                "warehouse/stock/*",
                "fts/v1/ff/*",
            ],
<<<<<<< HEAD
            order_ids={"2413eb6e-fb6b-4ed1-b93f-fb17143a4593"},
=======
            order_ids={
                "3adc738c-c149-4fed-8f83-8b00f84f5b92",
                "2413eb6e-fb6b-4ed1-b93f-fb17143a4593",
                "eb4d90bc-f842-4c59-9cff-07299bb78aa4",
                "efd17d7a-efb2-4892-9c6e-ed7bba7af3d5",
            },
>>>>>>> PR-09-completed-orders
            passthrough_patterns=["warehouse/stock"],
        ),
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--only",
        choices=[cfg.name for cfg in load_default_configs()],
        help="Build only the selected default fixture.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not write files, only report how many messages would be emitted.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    configs = load_default_configs()

    if args.only:
        configs = [cfg for cfg in configs if cfg.name == args.only]

    total = 0
    for config in configs:
        total += build_fixture(config, dry_run=args.dry_run)
    return 0 if total else 1


if __name__ == "__main__":
    raise SystemExit(main())

