#!/usr/bin/env python3
"""
Schema Test Runner - Automatisiertes Schema-Testing
Testet alle Topics systematisch und liefert detaillierte Ergebnisse
"""

import json
import traceback
from pathlib import Path
from typing import Any, Dict

from omf2.registry.manager.registry_manager import get_registry_manager


class SchemaTestRunner:
    def __init__(self):
        # Use absolute path from project root
        project_root = Path(__file__).parent.parent.parent.parent
        registry_path = project_root / "omf2" / "registry"
        self.registry_manager = get_registry_manager(str(registry_path))
        self.results = []

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Führt umfassenden Schema-Test durch"""
        print("🔍 Starting comprehensive schema test...")

        # Get all topics
        all_topics = self.registry_manager.get_topics()
        print(f"📊 Testing {len(all_topics)} topics...")

        valid_count = 0
        invalid_count = 0
        no_schema_count = 0
        errors = []

        for topic in all_topics:
            result = self._test_topic(topic)
            self.results.append(result)

            if result["status"] == "VALID":
                valid_count += 1
            elif result["status"] == "NO_SCHEMA":
                no_schema_count += 1
            else:
                invalid_count += 1
                errors.append(result)

        # Summary
        total = len(all_topics)
        summary = {
            "total_topics": total,
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "no_schema_count": no_schema_count,
            "valid_percentage": (valid_count / total) * 100 if total > 0 else 0,
            "invalid_percentage": (invalid_count / total) * 100 if total > 0 else 0,
            "no_schema_percentage": (no_schema_count / total) * 100 if total > 0 else 0,
            "errors": errors[:10],  # Top 10 errors
            "all_results": self.results,
        }

        return summary

    def _test_topic(self, topic: str) -> Dict[str, Any]:
        """Testet einen einzelnen Topic"""
        try:
            # Get schema for topic
            topic_schema = self.registry_manager.get_topic_schema(topic)

            if not topic_schema:
                return {"topic": topic, "status": "NO_SCHEMA", "error": "No schema found", "schema_file": None}

            # Generate test payload
            payload = self._generate_test_payload(topic, topic_schema)

            # Validate payload
            validation_result = self.registry_manager.validate_topic_payload(topic, payload)

            if validation_result.get("valid", False):
                return {
                    "topic": topic,
                    "status": "VALID",
                    "error": None,
                    "schema_file": (
                        topic_schema.get("$id", "unknown") if isinstance(topic_schema, dict) else str(topic_schema)
                    ),
                    "payload": payload,
                }
            else:
                return {
                    "topic": topic,
                    "status": "INVALID",
                    "error": validation_result.get("error", "Validation failed"),
                    "schema_file": (
                        topic_schema.get("$id", "unknown") if isinstance(topic_schema, dict) else str(topic_schema)
                    ),
                    "payload": payload,
                    "validation_errors": validation_result.get("errors", []),
                }

        except Exception as e:
            return {
                "topic": topic,
                "status": "ERROR",
                "error": str(e),
                "schema_file": None,
                "traceback": traceback.format_exc(),
            }

    def _generate_test_payload(self, topic: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generiert Test-Payload basierend auf Schema"""
        if isinstance(schema, str):
            # Load schema from file
            schema_path = self.registry_manager.registry_path / "schemas" / schema
            if schema_path.exists():
                with open(schema_path) as f:
                    schema = json.load(f)
            else:
                return {}

        if not isinstance(schema, dict):
            return {}

        # Generate payload based on schema properties
        payload = {}
        properties = schema.get("properties", {})
        required = schema.get("required", [])

        for prop, prop_info in properties.items():
            if prop in required or prop in ["orderUpdateId", "orderId", "operatingMode", "paused"]:
                payload[prop] = self._generate_property_value(prop, prop_info)

        return payload

    def _generate_property_value(self, prop: str, prop_info: Dict[str, Any]) -> Any:
        """Generiert Wert für eine Property"""
        prop_type = prop_info.get("type")

        # Handle specific properties
        if prop == "orderUpdateId":
            return 0
        elif prop == "orderId":
            return "test_order_123"
        elif prop == "operatingMode":
            return "AUTOMATIC"
        elif prop == "paused":
            return False
        elif prop == "loads":
            return [
                {"loadType": "WHITE", "loadId": "047c8bca341291", "loadPosition": "A1", "loadTimestamp": 1759220483909}
            ]
        elif prop == "actionStates":
            return [
                {
                    "id": "test_action",
                    "state": "FINISHED",
                    "command": "test_command",
                    "timestamp": "2024-01-01T00:00:00Z",
                    "metadata": {},
                }
            ]
        elif prop == "metadata":
            return {"opcuaState": "connected"}
        elif prop == "batteryState":
            return {"charging": True, "currentVoltage": 12.0, "maxVolt": 14.4, "minVolt": 10.0, "percentage": 85}
        elif prop == "navigationTypes":
            return ["example_nav1", "example_nav2"]
        elif prop == "typeSpecification":
            # Handle different typeSpecification requirements
            if "agvClass" in prop_info.get("properties", {}):
                return {
                    "agvClass": "test_agv_class",
                    "seriesName": "test_series",
                    "navigationTypes": ["example_nav1", "example_nav2"],
                }
            elif "moduleClass" in prop_info.get("properties", {}):
                return {"moduleClass": "test_module_class", "seriesName": "test_series"}
            else:
                return {}
        elif prop == "action":
            return {
                "id": "test_action_id",
                "command": "test_command",
                "metadata": {
                    "type": "test_type",
                    "workpieceId": "test_workpiece",
                    "duration": 1000,
                    "workpiece": {
                        "workpieceId": "test_workpiece",
                        "type": "test_type",
                        "state": "test_state",
                        "history": [{"ts": 1234567890, "code": 1}],
                    },
                },
            }

        # Handle by type
        if isinstance(prop_type, list):
            prop_type = prop_type[0]  # Take first type from union

        if prop_type == "string":
            return f"test_{prop}"
        elif prop_type == "integer":
            return 0
        elif prop_type == "number":
            return 0.0
        elif prop_type == "boolean":
            return False
        elif prop_type == "array":
            items = prop_info.get("items", {})
            if items.get("type") == "string":
                return ["example_item1", "example_item2"]
            return []
        elif prop_type == "object":
            return {}

        return None

    def export_results(self, output_file: str = "schema_test_results.json"):
        """Exportiert Ergebnisse zu JSON"""
        summary = self.run_comprehensive_test()

        output_path = Path(output_file)
        with open(output_path, "w") as f:
            json.dump(summary, f, indent=2)

        print(f"📁 Results exported to: {output_path}")
        return summary

    def print_summary(self):
        """Druckt Zusammenfassung"""
        summary = self.run_comprehensive_test()

        print("\n" + "=" * 60)
        print("📊 SCHEMA TEST SUMMARY")
        print("=" * 60)
        print(f"Total Topics: {summary['total_topics']}")
        print(f"✅ Valid: {summary['valid_count']} ({summary['valid_percentage']:.1f}%)")
        print(f"❌ Invalid: {summary['invalid_count']} ({summary['invalid_percentage']:.1f}%)")
        print(f"⚠️ No Schema: {summary['no_schema_count']} ({summary['no_schema_percentage']:.1f}%)")

        if summary["errors"]:
            print("\n🔍 TOP ERRORS:")
            for i, error in enumerate(summary["errors"][:5], 1):
                print(f"{i}. {error['topic']}: {error['error']}")

        print("=" * 60)


def main():
    """Hauptfunktion"""
    runner = SchemaTestRunner()

    # Run test and print summary
    runner.print_summary()

    # Export detailed results
    runner.export_results("schema_test_results.json")

    print("\n🎯 Use this data to fix schema issues systematically!")


if __name__ == "__main__":
    main()
