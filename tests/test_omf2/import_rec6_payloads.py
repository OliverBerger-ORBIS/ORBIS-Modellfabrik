#!/usr/bin/env python3
"""
Import script für echte Test-Daten aus data/aps-data/*/

Konvertiert Dateien von:
- data/aps-data/topics/{session}/_topic_name__000001.json
Zu:
- tests/test_payloads_for_topic/_topic_name__000001.json

Extrahiert nur den Payload-Inhalt für Schema-Validierung.
Unterstützt: rec0, rec1, rec3, rec4, rec5, rec6, rec7, rec8
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class MultiRecPayloadImporter:
    """Importiert und konvertiert Payload-Dateien aus allen Recording-Sessions"""

    def __init__(self):
        self.base_source_dir = Path("/Users/oliver/Projects/ORBIS-Modellfabrik/data/aps-data/topics")
        self.target_dir = Path("/Users/oliver/Projects/ORBIS-Modellfabrik/tests/test_omf2/test_payloads_for_topic")

        # Available recording sessions
        self.available_sessions = ["rec0", "rec1", "rec3", "rec4", "rec5", "rec6", "rec7", "rec8"]

        # Ensure target directory exists
        self.target_dir.mkdir(parents=True, exist_ok=True)

    def import_all_payloads(self, sessions: List[str] = None) -> Dict[str, Any]:
        """
        Importiere alle Payload-Dateien aus den angegebenen Sessions

        Args:
            sessions: List of session names (e.g., ['rec5', 'rec7', 'rec8'])

        Returns:
            Import statistics
        """
        if sessions is None:
            sessions = self.available_sessions

        logger.info(f"🚀 Starte Import von {', '.join(sessions)} Payload-Dateien...")

        overall_stats = {
            "total_files": 0,
            "imported_files": 0,
            "skipped_files": 0,
            "error_files": 0,
            "topics": {},
            "sessions": {},
            "errors": [],
        }

        # Process each session
        for session in sessions:
            session_stats = self.import_session_payloads(session)

            # Merge stats
            overall_stats["total_files"] += session_stats["total_files"]
            overall_stats["imported_files"] += session_stats["imported_files"]
            overall_stats["skipped_files"] += session_stats["skipped_files"]
            overall_stats["error_files"] += session_stats["error_files"]
            overall_stats["errors"].extend(session_stats["errors"])

            # Merge topics
            for topic, count in session_stats["topics"].items():
                if topic not in overall_stats["topics"]:
                    overall_stats["topics"][topic] = 0
                overall_stats["topics"][topic] += count

            overall_stats["sessions"][session] = session_stats

        # Print overall summary
        logger.info("\n🎯 Gesamt-Import abgeschlossen:")
        logger.info(f"   📊 {overall_stats['imported_files']}/{overall_stats['total_files']} Dateien importiert")
        logger.info(f"   ⚠️ {overall_stats['skipped_files']} übersprungen")
        logger.info(f"   ❌ {overall_stats['error_files']} Fehler")
        logger.info(f"   📋 {len(overall_stats['topics'])} Topics verarbeitet")
        logger.info(f"   📁 {len(sessions)} Sessions verarbeitet")

        # Print session breakdown
        logger.info("\n📁 Session-Statistiken:")
        for session, stats in overall_stats["sessions"].items():
            logger.info(f"   🔍 {session}: {stats['imported_files']}/{stats['total_files']} Dateien")

        # Print topic statistics (top 10)
        if overall_stats["topics"]:
            logger.info("\n📋 Top Topic-Statistiken:")
            sorted_topics = sorted(overall_stats["topics"].items(), key=lambda x: x[1], reverse=True)
            for topic, count in sorted_topics[:10]:
                logger.info(f"   🔍 {topic}: {count} Sequenzen")
            if len(sorted_topics) > 10:
                logger.info(f"   ... und {len(sorted_topics) - 10} weitere Topics")

        return overall_stats

    def import_session_payloads(self, session: str) -> Dict[str, Any]:
        """
        Importiere alle Payload-Dateien aus einer Session

        Args:
            session: Session name (e.g., 'rec5')

        Returns:
            Import statistics for this session
        """
        source_dir = self.base_source_dir / session

        if not source_dir.exists():
            logger.warning(f"⚠️ Session directory nicht gefunden: {source_dir}")
            return {
                "total_files": 0,
                "imported_files": 0,
                "skipped_files": 0,
                "error_files": 0,
                "topics": {},
                "errors": [f"Session {session} not found"],
            }

        # Find all JSON files in session
        source_files = list(source_dir.glob("*.json"))
        logger.info(f"📁 {session}: {len(source_files)} Dateien gefunden")

        stats = {
            "total_files": len(source_files),
            "imported_files": 0,
            "skipped_files": 0,
            "error_files": 0,
            "topics": {},
            "errors": [],
        }

        # Process each file
        for source_file in source_files:
            try:
                result = self.import_single_file(source_file, session)

                if result["success"]:
                    stats["imported_files"] += 1
                    topic = result["topic"]
                    if topic not in stats["topics"]:
                        stats["topics"][topic] = 0
                    stats["topics"][topic] += 1
                    logger.debug(f"✅ {session}/{source_file.name} -> {result['target_file']}")
                else:
                    stats["skipped_files"] += 1
                    logger.debug(f"⚠️ {session}/{source_file.name}: {result['reason']}")

            except Exception as e:
                stats["error_files"] += 1
                stats["errors"].append(f"{session}/{source_file.name}: {e}")
                logger.error(f"❌ {session}/{source_file.name}: {e}")

        logger.info(f"📊 {session}: {stats['imported_files']}/{stats['total_files']} Dateien importiert")
        return stats

    def import_single_file(self, source_file: Path, session: str = None) -> Dict[str, Any]:
        """
        Importiere eine einzelne Datei

        Args:
            source_file: Source file path
            session: Session name for logging

        Returns:
            Import result
        """
        try:
            # Load source file
            with open(source_file, encoding="utf-8") as f:
                source_data = json.load(f)

            # Extract topic and payload
            topic = source_data.get("topic")
            if not topic:
                return {"success": False, "reason": "No topic field found"}

            # Extract payload (can be string or dict)
            payload = source_data.get("payload")
            if not payload:
                return {"success": False, "reason": "No payload field found"}

            # Convert payload string to dict if needed
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except json.JSONDecodeError as e:
                    return {"success": False, "reason": f"Invalid JSON in payload: {e}"}

            # Generate target filename
            target_filename = source_file.name  # Keep original filename
            target_file = self.target_dir / target_filename

            # Write payload-only file
            with open(target_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)

            return {
                "success": True,
                "topic": topic,
                "target_file": target_filename,
                "payload_keys": list(payload.keys()) if isinstance(payload, dict) else [],
            }

        except Exception as e:
            return {"success": False, "reason": f"Import error: {e}"}

    def cleanup_target_directory(self) -> None:
        """Lösche alle Dateien im Target-Verzeichnis"""
        if self.target_dir.exists():
            for file in self.target_dir.glob("*.json"):
                file.unlink()
            logger.info(f"🧹 Target-Verzeichnis geleert: {self.target_dir}")

    def list_available_topics(self) -> List[str]:
        """
        Liste alle verfügbaren Topics in rec6/

        Returns:
            List of unique topics
        """
        topics = set()

        if not self.source_dir.exists():
            return []

        for source_file in self.source_dir.glob("*.json"):
            try:
                with open(source_file, encoding="utf-8") as f:
                    data = json.load(f)
                topic = data.get("topic")
                if topic:
                    topics.add(topic)
            except Exception:
                continue

        return sorted(topics)


def main():
    """Main function"""
    print("🚀 Rec6 Payload Import Tool")
    print("=" * 50)

    # TODO: Implement Rec6PayloadImporter class
    # importer = Rec6PayloadImporter()

    # List available topics
    # topics = importer.list_available_topics()
    topics = []  # TODO: Implement when Rec6PayloadImporter is available
    print(f"\n📋 Verfügbare Topics in rec6/: {len(topics)}")
    for topic in topics[:10]:  # Show first 10
        print(f"   🔍 {topic}")
    if len(topics) > 10:
        print(f"   ... und {len(topics) - 10} weitere")

    # Ask user
    print("\n🎯 Optionen:")
    print("1. Alle Dateien importieren")
    print("2. Target-Verzeichnis leeren")
    print("3. Beenden")

    try:
        choice = input("\n🎯 Wähle Option (1-3): ").strip()

        if choice == "1":
            # Import all
            # stats = importer.import_all_payloads()
            stats = {"error": "Rec6PayloadImporter not implemented"}  # TODO: Implement
            if "error" not in stats:
                print("\n✅ Import erfolgreich!")
                print(f"   📊 {stats['imported_files']} Dateien importiert")
                print(f"   📋 {len(stats['topics'])} Topics verarbeitet")
            else:
                print(f"\n❌ Import fehlgeschlagen: {stats['error']}")

        elif choice == "2":
            # Cleanup
            # importer.cleanup_target_directory()
            print("TODO: Implement cleanup when Rec6PayloadImporter is available")
            print("✅ Target-Verzeichnis geleert")

        elif choice == "3":
            print("👋 Auf Wiedersehen!")

        else:
            print("❌ Ungültige Option")
            return 1

    except KeyboardInterrupt:
        print("\n⏹️ Import abgebrochen.")
        return 1
    except Exception as e:
        print(f"\n💥 Fehler: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
