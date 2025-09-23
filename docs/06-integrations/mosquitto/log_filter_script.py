#!/usr/bin/env python3
"""
Log Filter Script für APS-Mosquitto Analyse
Filtert periodische/unwichtige Topics und behält nur die ersten 10 Beispiele pro Topic
"""

import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict


class LogFilter:
    """Filter für Mosquitto-Log-Dateien"""

    def __init__(self):
        # Periodische/unwichtige Topics (basierend auf Session Analyzer Vorfilter)
        self.periodic_topics = {
            "/j1/txt/1/i/cam",  # Kamera-Daten (sehr große Payloads)
            "/j1/txt/1/i/bme680",  # BME680-Sensor-Daten
            "/j1/txt/1/i/ldr",  # LDR-Sensor-Daten
            "/j1/txt/1/c/bme680",  # BME680-Sensor-Daten (andere Schreibweise)
            "/j1/txt/1/c/cam",  # Kamera-Daten (andere Schreibweise)
            "/j1/txt/1/c/ldr",  # LDR-Sensor-Daten (andere Schreibweise)
        }

        # Wichtige Topics die komplett behalten werden
        self.important_topics = {
            "ccu/order/request",  # Auftragsanfragen
            "ccu/order/active",  # Aktive Aufträge
            "ccu/order/completed",  # Abgeschlossene Aufträge
            "ccu/state/",  # CCU-Status
            "ccu/pairing/state",  # Pairing-Status
            "module/v1/ff/",  # Module-Status und Commands
            "fts/v1/ff/",  # FTS-Status
            "instantAction",  # Instant Actions
            "factory",  # Factory Reset
            "charge",  # FTS Charge
        }

        # Topic-Counter für periodische Topics
        self.topic_counters: Dict[str, int] = defaultdict(int)
        self.max_examples_per_topic = 10

    def is_periodic_topic(self, topic: str) -> bool:
        """Prüft ob ein Topic zu den periodischen Topics gehört"""
        return any(periodic_topic in topic for periodic_topic in self.periodic_topics)

    def is_important_topic(self, topic: str) -> bool:
        """Prüft ob ein Topic zu den wichtigen Topics gehört"""
        return any(important_topic in topic for important_topic in self.important_topics)

    def should_keep_line(self, line: str) -> bool:
        """Entscheidet ob eine Log-Zeile behalten werden soll"""
        # Extrahiere Topic aus der Log-Zeile
        topic = self.extract_topic_from_line(line)
        if not topic:
            return True  # Zeilen ohne Topic behalten (z.B. Timestamps, Connect/Disconnect)

        # Wichtige Topics immer behalten
        if self.is_important_topic(topic):
            return True

        # Periodische Topics: Nur erste 10 Beispiele behalten
        if self.is_periodic_topic(topic):
            self.topic_counters[topic] += 1
            return self.topic_counters[topic] <= self.max_examples_per_topic

        # Alle anderen Topics behalten
        return True

    def extract_topic_from_line(self, line: str) -> str:
        """Extrahiert das Topic aus einer Log-Zeile"""
        # Verschiedene Log-Formate unterstützen

        # Format 1: "1758097605: Sending PUBLISH to client (d0, q1, r1, m245, 'topic', ... (84 bytes))"
        match = re.search(r"'([^']+)'", line)
        if match:
            return match.group(1)

        # Format 2: "topic payload" (direktes Format)
        if ' ' in line and not line.startswith(('1758', '2025')):
            return line.split(' ')[0]

        # Format 3: "1758097605: Received PUBLISH from client (d0, q1, r1, m245, 'topic', ... (84 bytes))"
        match = re.search(r"Received PUBLISH.*?'([^']+)'", line)
        if match:
            return match.group(1)

        return ""

    def filter_log_file(self, input_file: Path, output_file: Path) -> Dict[str, int]:
        """Filtert eine Log-Datei und erstellt eine gefilterte Version"""
        stats = {
            "total_lines": 0,
            "kept_lines": 0,
            "filtered_lines": 0,
            "periodic_topics_found": set(),
            "important_topics_found": set(),
        }

        print(f"🔍 Filtere Log-Datei: {input_file}")
        print(f"📝 Ausgabe-Datei: {output_file}")

        with open(input_file, encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:

            for line_num, line in enumerate(infile, 1):
                stats["total_lines"] += 1

                if line_num % 10000 == 0:
                    print(f"📊 Verarbeitet: {line_num:,} Zeilen...")

                if self.should_keep_line(line):
                    outfile.write(line)
                    stats["kept_lines"] += 1

                    # Topic-Statistiken sammeln
                    topic = self.extract_topic_from_line(line)
                    if topic:
                        if self.is_periodic_topic(topic):
                            stats["periodic_topics_found"].add(topic)
                        elif self.is_important_topic(topic):
                            stats["important_topics_found"].add(topic)
                else:
                    stats["filtered_lines"] += 1

        return stats

    def print_filter_stats(self, stats: Dict[str, int]):
        """Druckt Filter-Statistiken"""
        print("\n📊 Filter-Statistiken:")
        print(f"   Gesamt-Zeilen: {stats['total_lines']:,}")
        print(f"   Behalten: {stats['kept_lines']:,}")
        print(f"   Gefiltert: {stats['filtered_lines']:,}")
        print(f"   Filter-Rate: {(stats['filtered_lines']/stats['total_lines']*100):.1f}%")

        print(f"\n🔍 Periodische Topics gefunden: {len(stats['periodic_topics_found'])}")
        for topic in sorted(stats['periodic_topics_found']):
            count = self.topic_counters.get(topic, 0)
            print(f"   - {topic}: {count} Beispiele behalten")

        print(f"\n⭐ Wichtige Topics gefunden: {len(stats['important_topics_found'])}")
        for topic in sorted(stats['important_topics_found']):
            print(f"   - {topic}")


def main():
    """Hauptfunktion"""
    if len(sys.argv) != 3:
        print("Usage: python log_filter_script.py <input_log> <output_log>")
        print("Example: python log_filter_script.py mosquitto_aps_analysis.log mosquitto_filtered.log")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    if not input_file.exists():
        print(f"❌ Eingabe-Datei nicht gefunden: {input_file}")
        sys.exit(1)

    filter_tool = LogFilter()
    stats = filter_tool.filter_log_file(input_file, output_file)
    filter_tool.print_filter_stats(stats)

    print(f"\n✅ Gefilterte Log-Datei erstellt: {output_file}")
    print(f"📏 Dateigröße: {output_file.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
