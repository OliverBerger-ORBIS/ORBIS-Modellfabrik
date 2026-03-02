#!/usr/bin/env python3
"""
Aggregiert Statistiken aus allen Modul-Analysen (HBW, DRILL, MILL, DPS, AIQS)

Erstellt eine Gesamt-Übersicht ähnlich ANALYSIS_SUMMARY.md, aber für alle Module.
"""

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

MODULES = {
    "hbw": {"serial": "SVR3QA0022", "analysis_dir": "data/osf-data/hbw-analysis"},
    "drill": {"serial": "SVR4H76449", "analysis_dir": "data/osf-data/drill-analysis"},
    "mill": {"serial": "SVR3QA2098", "analysis_dir": "data/osf-data/mill-analysis"},
    "dps": {"serial": "SVR4H73275", "analysis_dir": "data/osf-data/dps-analysis"},
    "aiqs": {"serial": "SVR4H76530", "analysis_dir": "data/osf-data/aiqs-analysis"},
}


def load_metadata_files(analysis_dir: Path) -> List[Dict[str, Any]]:
    """Lädt alle Metadata-Dateien aus einem Analysis-Verzeichnis"""
    metadata_files = list(analysis_dir.glob("*_metadata.json"))
    metadata_list = []

    for metadata_file in metadata_files:
        try:
            with open(metadata_file, encoding="utf-8") as f:
                metadata = json.load(f)
                metadata_list.append(metadata)
        except Exception as e:
            print(f"⚠️  Fehler beim Laden von {metadata_file}: {e}", file=sys.stderr)
            continue

    return metadata_list


def aggregate_module_stats(module_name: str, analysis_dir: Path) -> Dict[str, Any]:
    """Aggregiert Statistiken für ein Modul"""
    metadata_list = load_metadata_files(analysis_dir)

    if not metadata_list:
        return {
            "module": module_name,
            "sessions_analyzed": 0,
            "total_messages": 0,
            "module_relevant_messages": 0,
            "commands": {},
            "operations_count": 0,
            "order_context_count": 0,
        }

    # Aggregiere Statistiken
    total_messages = sum(m.get("total_messages", 0) for m in metadata_list)
    module_relevant_messages = sum(m.get(f"{module_name}_relevant_messages", 0) for m in metadata_list)

    # Commands aggregieren
    commands_counter = Counter()
    for metadata in metadata_list:
        commands_found = metadata.get("commands_found", {})
        for command, count in commands_found.items():
            commands_counter[command] += count

    # Operations aggregieren
    if module_name == "hbw":
        operations_key = "storage_operations_count"
    elif module_name == "drill":
        operations_key = "drill_operations_count"
    elif module_name == "mill":
        operations_key = "mill_operations_count"
    elif module_name == "dps":
        operations_key = None  # DPS hat keine operations_count, sondern storage/production context
    elif module_name == "aiqs":
        operations_key = "check_quality_results_count"
    else:
        operations_key = None

    operations_count = sum(m.get(operations_key, 0) for m in metadata_list) if operations_key else 0

    # Order Context aggregieren
    if module_name in ["hbw"]:
        order_context_key = "storage_order_context_count"
    elif module_name in ["drill", "mill"]:
        order_context_key = "production_order_context_count"
    elif module_name == "dps":
        order_context_key = "storage_order_context_count"  # DPS hat beide
    elif module_name == "aiqs":
        order_context_key = "check_quality_context_count"
    else:
        order_context_key = None

    order_context_count = sum(m.get(order_context_key, 0) for m in metadata_list) if order_context_key else 0

    return {
        "module": module_name.upper(),
        "sessions_analyzed": len(metadata_list),
        "total_messages": total_messages,
        "module_relevant_messages": module_relevant_messages,
        "commands": dict(commands_counter),
        "operations_count": operations_count,
        "order_context_count": order_context_count,
    }


def main():
    project_root = Path(__file__).parent.parent
    output_file = project_root / "data/osf-data/MODULE_ANALYSIS_SUMMARY.md"

    all_stats = {}

    print("📊 Aggregiere Statistiken für alle Module...\n")

    for module_name, config in MODULES.items():
        analysis_dir = project_root / config["analysis_dir"]
        stats = aggregate_module_stats(module_name, analysis_dir)
        all_stats[module_name] = stats

        print(f"✅ {module_name.upper()}:")
        print(f"   Sessions: {stats['sessions_analyzed']}")
        print(f"   Module-relevante Messages: {stats['module_relevant_messages']}")
        print(f"   Operations: {stats['operations_count']}")
        commands_str = ", ".join(
            f"{cmd}({count})" for cmd, count in sorted(stats["commands"].items(), key=lambda x: x[1], reverse=True)
        )
        print(f"   Commands: {commands_str}")
        print()

    # Erstelle Markdown-Dokumentation
    md_content = f"""# Module Analysis Summary

Diese Datei enthält aggregierte Statistiken aus allen Modul-Analysen (HBW, DRILL, MILL, DPS, AIQS).

**Erstellt:** {Path(__file__).stat().st_mtime}
**Sessions analysiert:** 13 Session-Log-Dateien

## Übersicht

| Modul | Serial | Sessions | Module-Messages | Operations | Haupt-Commands |
|-------|--------|----------|-----------------|-----------|----------------|
"""

    for module_name, stats in all_stats.items():
        config = MODULES[module_name]
        top_commands = ", ".join(
            [
                f"{cmd}({count})"
                for cmd, count in sorted(stats["commands"].items(), key=lambda x: x[1], reverse=True)[:3]
            ]
        )
        md_content += f"| {stats['module']} | {config['serial']} | {stats['sessions_analyzed']} | {stats['module_relevant_messages']} | {stats['operations_count']} | {top_commands} |\n"

    md_content += "\n## Detaillierte Statistiken\n\n"

    for module_name, stats in all_stats.items():
        config = MODULES[module_name]
        md_content += f"""### {stats['module']} (Serial: {config['serial']})

- **Sessions analysiert:** {stats['sessions_analyzed']}
- **Gesamt-Messages (alle Sessions):** {stats['total_messages']}
- **{stats['module']}-relevante Messages:** {stats['module_relevant_messages']}
- **Operations gefunden:** {stats['operations_count']}
- **Order-Context Messages:** {stats['order_context_count']}

**Commands gefunden:**
"""
        for command, count in sorted(stats["commands"].items(), key=lambda x: x[1], reverse=True):
            md_content += f"- `{command}`: {count}x\n"

        md_content += "\n"

    md_content += """## Nächste Schritte

Diese Daten werden verwendet, um:
1. Modul-spezifische Beispiel-Anwendungen zu entwickeln
2. Status-Visualisierungen zu erstellen
3. Command-History-Features zu implementieren
4. Integration in OSF Shopfloor-Tab vorzubereiten

## Verwandte Dokumentation

- [DPS Analysis README](./dps-analysis/README.md)
- [AIQS Analysis README](./aiqs-analysis/README.md)
- [HBW Analysis README](./hbw-analysis/README.md)
- [DRILL Analysis README](./drill-analysis/README.md)
- [MILL Analysis README](./mill-analysis/README.md)
- [GitHub Requirement](./GITHUB_REQUIREMENT.md)
"""

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"✅ Gesamt-Statistiken gespeichert: {output_file}")


if __name__ == "__main__":
    main()
