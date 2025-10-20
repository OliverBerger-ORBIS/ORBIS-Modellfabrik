#!/usr/bin/env python3
"""
Systematischer Test für Schema-Validierung aller Topics in der Registry

Testet für jedes Topic in der Registry:
1. Schema aus registry/*.yml laden
2. Test-Payload aus tests/test_payloads_for_topic/_<topic_name>.json laden
3. Schema-Validation mit Registry Manager testen

Beispiel: Topic "/j1/txt/1/c/cam"
- Schema: j1_txt_1_c_cam.schema.json (aus txt.yml)
- Payload: _j1_txt_1_c_cam.json
- Validation: registry_manager.validate_topic_payload()
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add omf2 to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from omf2.common.logger import get_logger
from omf2.registry.manager.registry_manager import get_registry_manager

logger = get_logger(__name__)


class SchemaValidationTester:
    """Systematischer Tester für Schema-Validierung aller Topics"""

    def __init__(self):
        """Initialize Schema Validation Tester"""
        self.registry_manager = get_registry_manager()
        self.test_payloads_dir = Path(__file__).parent / "test_payloads_for_topic"

        # Ensure test payloads directory exists
        self.test_payloads_dir.mkdir(exist_ok=True)

        logger.info("🧪 Schema Validation Tester initialized")

    def get_all_topics_from_registry(self) -> List[str]:
        """
        Hole alle Topics aus der Registry

        Returns:
            List of topic names from all registry files
        """
        all_topics = self.registry_manager.get_topics()
        logger.info(f"📡 Found {len(all_topics)} topics in registry")
        return all_topics

    def topic_name_to_filename(self, topic: str) -> str:
        """
        Konvertiere Topic-Name zu Dateiname

        Args:
            topic: Topic name (e.g., "/j1/txt/1/c/cam")

        Returns:
            Filename (e.g., "_j1_txt_1_c_cam.json")
        """
        # Remove leading slash and replace remaining slashes with underscores
        filename = topic.lstrip("/").replace("/", "_")
        return f"_{filename}.json"

    def find_test_payload_files(self, topic: str) -> List[Path]:
        """
        Finde alle Test-Payload-Dateien für Topic (inklusive Sequenz-Nummern)

        Args:
            topic: Topic name

        Returns:
            Liste aller gefundenen Dateien
        """
        base_filename = topic.lstrip("/").replace("/", "_")
        found_files = []

        # Pattern für Sequenz-Nummern: topic_name__000001.json (ohne führenden Unterstrich)
        sequence_pattern = f"{base_filename}__*.json"
        sequence_files = list(self.test_payloads_dir.glob(sequence_pattern))
        found_files.extend(sequence_files)

        # Fallback: Einzelne Datei ohne Sequenz
        single_patterns = [
            f"_{base_filename}.json",  # Original pattern
            f"{base_filename}.json",  # Without underscore
            f"{topic.replace('/', '_')}.json",  # With leading slash converted
        ]

        for pattern in single_patterns:
            payload_path = self.test_payloads_dir / pattern
            if payload_path.exists() and payload_path not in found_files:
                found_files.append(payload_path)
                break

        return sorted(found_files)

    def find_test_payload_file(self, topic: str) -> Optional[Path]:
        """
        Finde erste Test-Payload-Datei für Topic (für Backward Compatibility)

        Args:
            topic: Topic name

        Returns:
            Path zur ersten gefundenen Datei oder None
        """
        files = self.find_test_payload_files(topic)
        return files[0] if files else None

    def load_test_payload(self, topic: str) -> Optional[Dict[str, Any]]:
        """
        Lade Test-Payload für Topic

        Args:
            topic: Topic name

        Returns:
            Test payload data or None if not found
        """
        payload_path = self.find_test_payload_file(topic)

        if not payload_path:
            logger.warning(f"⚠️ Test payload not found for topic: {topic}")
            return None

        try:
            with open(payload_path, encoding="utf-8") as f:
                test_data = json.load(f)
            logger.debug(f"📁 Loaded test payload for {topic}: {payload_path.name}")
            return test_data
        except Exception as e:
            logger.error(f"❌ Failed to load test payload for {topic}: {e}")
            return None

    def test_single_topic_validation(self, topic: str) -> Dict[str, Any]:
        """
        Teste Schema-Validierung für ein einzelnes Topic

        Args:
            topic: Topic name

        Returns:
            Test result dictionary
        """
        result = {
            "topic": topic,
            "status": "UNKNOWN",
            "error": None,
            "schema_file": None,
            "payload_file": None,
            "validation_result": None,
        }

        try:
            # 1. Get schema for topic
            schema = self.registry_manager.get_topic_schema(topic)
            if not schema:
                result["status"] = "NO_SCHEMA"
                result["error"] = "No schema found for topic"
                return result

            # Get schema file info
            topic_info = self.registry_manager.topics.get(topic, {})
            result["schema_file"] = topic_info.get("schema", "unknown")

            # 2. Load test payload
            test_data = self.load_test_payload(topic)
            if not test_data:
                result["status"] = "NO_PAYLOAD"
                result["error"] = "No test payload found"
                return result

            result["payload_file"] = self.topic_name_to_filename(topic)

            # 3. Load payload directly (Datei enthält nur noch den Payload!)
            payload = test_data  # test_data ist bereits der Payload!

            # 4. Test schema validation (validiert den Payload direkt)
            validation_result = self.registry_manager.validate_topic_payload(topic, payload)
            result["validation_result"] = validation_result

            if validation_result.get("valid", False):
                result["status"] = "VALID"
                result["error"] = None
            else:
                result["status"] = "INVALID"
                result["error"] = validation_result.get("error", "Validation failed")

        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)

        return result

    def test_topic_with_sequences(self, topic: str) -> Dict[str, Any]:
        """
        Teste Schema-Validierung für Topic mit allen Sequenzen

        Args:
            topic: Topic name

        Returns:
            Validierungsergebnis mit Sequenz-Details
        """
        result = {
            "topic": topic,
            "status": "UNKNOWN",
            "schema_file": None,
            "total_sequences": 0,
            "valid_sequences": 0,
            "invalid_sequences": 0,
            "sequences": [],
            "error": None,
        }

        # 1. Get topic schema
        schema = self.registry_manager.get_topic_schema(topic)
        if not schema:
            result["status"] = "NO_SCHEMA"
            result["error"] = "No schema found for topic"
            return result

        topic_info = self.registry_manager.topics.get(topic, {})
        result["schema_file"] = topic_info.get("schema", "unknown")

        # 2. Find all payload files for this topic
        payload_files = self.find_test_payload_files(topic)
        if not payload_files:
            result["status"] = "NO_PAYLOAD"
            result["error"] = "No test payload files found"
            return result

        result["total_sequences"] = len(payload_files)

        # 3. Test each payload file
        for payload_file in payload_files:
            try:
                with open(payload_file, encoding="utf-8") as f:
                    test_data = json.load(f)

                # Extract payload directly
                payload = test_data

                # Validate payload
                validation_result = self.registry_manager.validate_topic_payload(topic, payload)

                sequence_result = {
                    "file": payload_file.name,
                    "valid": validation_result.get("valid", False),
                    "error": validation_result.get("error") if not validation_result.get("valid", False) else None,
                }

                result["sequences"].append(sequence_result)

                if sequence_result["valid"]:
                    result["valid_sequences"] += 1
                else:
                    result["invalid_sequences"] += 1

            except Exception as e:
                sequence_result = {"file": payload_file.name, "valid": False, "error": f"Failed to load/validate: {e}"}
                result["sequences"].append(sequence_result)
                result["invalid_sequences"] += 1

        # 4. Determine overall status
        if result["total_sequences"] == 0:
            result["status"] = "NO_PAYLOAD"
        elif result["invalid_sequences"] == 0:
            result["status"] = "ALL_VALID"
        elif result["valid_sequences"] == 0:
            result["status"] = "ALL_INVALID"
        else:
            result["status"] = "MIXED"

        return result

    def run_sequence_comprehensive_test(self) -> Dict[str, Any]:
        """
        Führe systematischen Test für alle Topics mit Sequenz-Support durch

        Returns:
            Comprehensive test results with sequence details
        """
        logger.info("🚀 Starte systematischen Schema-Validierungstest mit Sequenzen...")

        # Get all topics from registry
        all_topics = self.get_all_topics_from_registry()
        logger.info(f"📊 Gefunden: {len(all_topics)} Topics im Registry")

        results = {
            "total_topics": len(all_topics),
            "tested_topics": 0,
            "valid_topics": 0,
            "invalid_topics": 0,
            "no_payload_topics": 0,
            "no_schema_topics": 0,
            "total_sequences": 0,
            "valid_sequences": 0,
            "invalid_sequences": 0,
            "topic_results": [],
            "summary": {},
        }

        # Test each topic
        for topic in all_topics:
            logger.info(f"🧪 Teste Topic: {topic}")

            # Use new sequence-aware testing
            result = self.test_topic_with_sequences(topic)
            results["topic_results"].append(result)
            results["tested_topics"] += 1

            # Update sequence statistics
            results["total_sequences"] += result.get("total_sequences", 0)
            results["valid_sequences"] += result.get("valid_sequences", 0)
            results["invalid_sequences"] += result.get("invalid_sequences", 0)

            if result["status"] == "ALL_VALID":
                results["valid_topics"] += 1
                logger.info(f"✅ {topic}: ALL_VALID ({result['valid_sequences']} Sequenzen)")
            elif result["status"] == "ALL_INVALID":
                results["invalid_topics"] += 1
                logger.warning(f"❌ {topic}: ALL_INVALID ({result['invalid_sequences']} Sequenzen)")
            elif result["status"] == "MIXED":
                results["invalid_topics"] += 1
                logger.warning(
                    f"⚠️ {topic}: MIXED ({result['valid_sequences']}/{result['total_sequences']} Sequenzen valid)"
                )
            elif result["status"] == "NO_PAYLOAD":
                results["no_payload_topics"] += 1
                logger.warning(f"⚠️ {topic}: NO_PAYLOAD")
            elif result["status"] == "NO_SCHEMA":
                results["no_schema_topics"] += 1
                logger.warning(f"⚠️ {topic}: NO_SCHEMA")

        # Generate summary
        results["summary"] = {
            "success_rate": (
                (results["valid_topics"] / results["tested_topics"] * 100) if results["tested_topics"] > 0 else 0
            ),
            "coverage": (
                (results["tested_topics"] / results["total_topics"] * 100) if results["total_topics"] > 0 else 0
            ),
            "sequence_success_rate": (
                (results["valid_sequences"] / results["total_sequences"] * 100) if results["total_sequences"] > 0 else 0
            ),
        }

        logger.info("🎯 Test abgeschlossen:")
        logger.info(f"   📊 {results['tested_topics']}/{results['total_topics']} Topics getestet")
        logger.info(f"   📋 {results['total_sequences']} Sequenzen insgesamt")
        logger.info(f"   ✅ {results['valid_topics']} Topics vollständig valid")
        logger.info(f"   ❌ {results['invalid_topics']} Topics mit Problemen")
        logger.info(f"   ⚠️ {results['no_payload_topics']} ohne Payload")
        logger.info(f"   ⚠️ {results['no_schema_topics']} ohne Schema")
        logger.info(f"   📈 Topic-Erfolgsrate: {results['summary']['success_rate']:.1f}%")
        logger.info(f"   📈 Sequenz-Erfolgsrate: {results['summary']['sequence_success_rate']:.1f}%")

        return results

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """
        Führe systematischen Test für alle Topics durch

        Returns:
            Comprehensive test results
        """
        logger.info("🚀 Starting comprehensive schema validation test...")

        # Get all topics
        all_topics = self.get_all_topics_from_registry()

        # Test each topic
        results = []
        valid_count = 0
        invalid_count = 0
        no_schema_count = 0
        no_payload_count = 0
        error_count = 0

        for topic in all_topics:
            logger.info(f"🔍 Testing topic: {topic}")
            result = self.test_single_topic_validation(topic)
            results.append(result)

            # Count results
            if result["status"] == "VALID":
                valid_count += 1
                logger.info(f"✅ {topic}: VALID")
            elif result["status"] == "INVALID":
                invalid_count += 1
                logger.warning(f"❌ {topic}: INVALID - {result['error']}")
            elif result["status"] == "NO_SCHEMA":
                no_schema_count += 1
                logger.warning(f"⚠️ {topic}: NO_SCHEMA")
            elif result["status"] == "NO_PAYLOAD":
                no_payload_count += 1
                logger.warning(f"📁 {topic}: NO_PAYLOAD")
            elif result["status"] == "ERROR":
                error_count += 1
                logger.error(f"💥 {topic}: ERROR - {result['error']}")

        # Summary
        total = len(all_topics)
        summary = {
            "total_topics": total,
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "no_schema_count": no_schema_count,
            "no_payload_count": no_payload_count,
            "error_count": error_count,
            "valid_percentage": (valid_count / total) * 100 if total > 0 else 0,
            "invalid_percentage": (invalid_count / total) * 100 if total > 0 else 0,
            "results": results,
        }

        logger.info(f"📊 Test Summary: {valid_count}/{total} topics valid ({summary['valid_percentage']:.1f}%)")

        return summary

    def print_detailed_results(self, summary: Dict[str, Any]):
        """
        Drucke detaillierte Testergebnisse

        Args:
            summary: Test results summary
        """
        print("\n" + "=" * 80)
        print("🧪 SYSTEMATISCHER SCHEMA-VALIDIERUNGS-TEST")
        print("=" * 80)

        # Summary
        print("\n📊 SUMMARY:")
        print(f"  Total Topics: {summary['total_topics']}")
        print(f"  ✅ Valid: {summary['valid_count']} ({summary['valid_percentage']:.1f}%)")
        print(f"  ❌ Invalid: {summary['invalid_count']} ({summary['invalid_percentage']:.1f}%)")
        print(f"  ⚠️ No Schema: {summary['no_schema_count']}")
        print(f"  📁 No Payload: {summary['no_payload_count']}")
        print(f"  💥 Errors: {summary['error_count']}")

        # Detailed results
        print("\n📋 DETAILED RESULTS:")
        for result in summary["results"]:
            status_icon = {
                "VALID": "✅",
                "INVALID": "❌",
                "NO_SCHEMA": "⚠️",
                "NO_PAYLOAD": "📁",
                "ERROR": "💥",
                "INVALID_JSON": "🔧",
            }.get(result["status"], "❓")

            print(f"  {status_icon} {result['topic']}")
            print(f"      Status: {result['status']}")
            if result["schema_file"]:
                print(f"      Schema: {result['schema_file']}")
            if result["payload_file"]:
                print(f"      Payload: {result['payload_file']}")
            if result["error"]:
                print(f"      Error: {result['error']}")
            print()


def main():
    """Main function - Test with sequence support"""
    print("🚀 Starte Schema-Validierungstest für alle Topics...")

    # Initialize tester
    tester = SchemaValidationTester()

    # Ask user which test to run
    print("\n📋 Verfügbare Test-Modi:")
    print("1. Standard-Test (eine Datei pro Topic)")
    print("2. Sequenz-Test (mehrere Dateien pro Topic)")

    try:
        choice = input("\n🎯 Wähle Test-Modus (1 oder 2): ").strip()

        if choice == "2":
            print("\n🧪 Führe Sequenz-Test durch...")
            results = tester.run_sequence_comprehensive_test()
            print_sequence_results(results)
        else:
            print("\n🧪 Führe Standard-Test durch...")
            results = tester.run_comprehensive_test()
            print_standard_results(results)

    except KeyboardInterrupt:
        print("\n⏹️ Test abgebrochen.")
        return 1
    except Exception as e:
        print(f"\n💥 Fehler beim Test: {e}")
        return 1

    return 0


def print_sequence_results(results):
    """Drucke Ergebnisse für Sequenz-Test"""
    print("\n" + "=" * 60)
    print("📊 SEQUENZ-TEST-ZUSAMMENFASSUNG")
    print("=" * 60)
    print(f"📈 Topic-Erfolgsrate: {results['summary']['success_rate']:.1f}%")
    print(f"📈 Sequenz-Erfolgsrate: {results['summary']['sequence_success_rate']:.1f}%")
    print(f"📊 Abdeckung: {results['summary']['coverage']:.1f}%")
    print(f"📋 {results['total_sequences']} Sequenzen insgesamt")
    print(f"✅ {results['valid_sequences']} Sequenzen valid")
    print(f"❌ {results['invalid_sequences']} Sequenzen invalid")
    print(f"✅ {results['valid_topics']} Topics vollständig valid")
    print(f"❌ {results['invalid_topics']} Topics mit Problemen")
    print(f"⚠️ {results['no_payload_topics']} ohne Payload")
    print(f"⚠️ {results['no_schema_topics']} ohne Schema")

    # Print detailed results for topics with issues
    print("\n" + "=" * 60)
    print("❌ TOPICS MIT PROBLEMEN")
    print("=" * 60)
    for result in results["topic_results"]:
        if result["status"] in ["ALL_INVALID", "MIXED", "NO_SCHEMA", "NO_PAYLOAD"]:
            print(f"\n🔍 {result['topic']}: {result['status']}")
            if result["status"] in ["ALL_INVALID", "MIXED"]:
                print(
                    f"   📋 {result['total_sequences']} Sequenzen: {result['valid_sequences']} valid, {result['invalid_sequences']} invalid"
                )
                for seq in result["sequences"]:
                    if not seq["valid"]:
                        print(f"   ❌ {seq['file']}: {seq['error']}")
            elif result["status"] == "NO_SCHEMA":
                print("   ⚠️ Kein Schema gefunden")
            elif result["status"] == "NO_PAYLOAD":
                print("   📁 Kein Test-Payload gefunden")


def print_standard_results(results):
    """Drucke Ergebnisse für Standard-Test"""
    print("\n" + "=" * 60)
    print("📊 TEST-ZUSAMMENFASSUNG")
    print("=" * 60)
    print(f"📈 Erfolgsrate: {results['valid_percentage']:.1f}%")
    print(f"✅ Valid: {results['valid_count']}")
    print(f"❌ Invalid: {results['invalid_count']}")
    print(f"⚠️ Kein Schema: {results['no_schema_count']}")
    print(f"📁 Kein Payload: {results['no_payload_count']}")
    print(f"💥 Fehler: {results['error_count']}")

    # Print detailed results for invalid topics
    print("\n" + "=" * 60)
    print("❌ INVALIDE TOPICS")
    print("=" * 60)
    for result in results["results"]:
        if result["status"] == "INVALID":
            print(f"🔍 {result['topic']}: {result['error']}")
        elif result["status"] == "NO_SCHEMA":
            print(f"⚠️ {result['topic']}: Kein Schema gefunden")
        elif result["status"] == "NO_PAYLOAD":
            print(f"📁 {result['topic']}: Kein Test-Payload gefunden")

    print("\n🎯 Test abgeschlossen!")


if __name__ == "__main__":
    exit(main())
