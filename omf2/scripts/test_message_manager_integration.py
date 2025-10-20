#!/usr/bin/env python3
"""
Task 2.9-E: Live-Modus Test Implementation
Test MessageManager-Integration in Replay Environment
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import after path setup (E402: Module level import not at top of file)
try:
    from omf2.common.message_manager import MessageManager
    from omf2.registry.manager.registry_manager import get_registry_manager
    from omf2.ui.common.components.payload_generator import PayloadGenerator
    from omf2.ui.common.components.schema_tester import SchemaTester
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


class MessageManagerIntegrationTester:
    """Test MessageManager-Integration in Replay Environment"""

    def __init__(self):
        self.registry_manager = get_registry_manager()
        self.admin_message_manager = MessageManager("admin", self.registry_manager)
        self.ccu_message_manager = MessageManager("ccu", self.registry_manager)
        self.payload_generator = PayloadGenerator(self.registry_manager)
        self.schema_tester = SchemaTester(self.registry_manager)

        self.test_results = {"total_tests": 0, "passed_tests": 0, "failed_tests": 0, "test_details": []}

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all MessageManager integration tests"""
        print("🧪 Starting MessageManager Integration Tests...")

        # Test 1: Schema-driven Payload Generation
        self._test_schema_driven_generation()

        # Test 2: MessageManager Validation (Admin Domain)
        self._test_admin_message_validation()

        # Test 3: MessageManager Validation (CCU Domain)
        self._test_ccu_message_validation()

        # Test 4: PayloadGenerator Quality
        self._test_payload_generator_quality()

        # Test 5: Schema Tester Consistency
        self._test_schema_tester_consistency()

        return self.test_results

    def _test_schema_driven_generation(self):
        """Test 1: Schema-driven Payload Generation"""
        print("\n📋 Test 1: Schema-driven Payload Generation")

        test_topics = [
            "ccu/status/health",
            "ccu/state/config",
            "ccu/order/request",
            "module/v1/ff/SVR4H76530/connection",
            "fts/v1/ff/5iO4/state",
        ]

        for topic in test_topics:
            self.test_results["total_tests"] += 1

            try:
                # Generate payload using PayloadGenerator
                payload = self.payload_generator.generate_example_payload(topic)

                if payload:
                    self.test_results["passed_tests"] += 1
                    self.test_results["test_details"].append(
                        {"test": f"Schema-driven generation for {topic}", "status": "PASSED", "payload": payload}
                    )
                    print(f"  ✅ {topic}: Payload generated successfully")
                else:
                    self.test_results["failed_tests"] += 1
                    self.test_results["test_details"].append(
                        {
                            "test": f"Schema-driven generation for {topic}",
                            "status": "FAILED",
                            "error": "No payload generated",
                        }
                    )
                    print(f"  ❌ {topic}: No payload generated")

            except Exception as e:
                self.test_results["failed_tests"] += 1
                self.test_results["test_details"].append(
                    {"test": f"Schema-driven generation for {topic}", "status": "FAILED", "error": str(e)}
                )
                print(f"  ❌ {topic}: {e}")

    def _test_admin_message_validation(self):
        """Test 2: MessageManager Validation (Admin Domain)"""
        print("\n📋 Test 2: Admin MessageManager Validation")

        test_cases = [
            {"topic": "ccu/status/health", "payload": {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}},
            {"topic": "ccu/state/config", "payload": {"maxParallelOrders": 5, "timeout": 30}},
            {"topic": "ccu/order/request", "payload": {"orderId": "ORD-001", "product": "Widget", "quantity": 10}},
        ]

        for test_case in test_cases:
            self.test_results["total_tests"] += 1

            try:
                validation_result = self.admin_message_manager.validate_message(
                    test_case["topic"], test_case["payload"]
                )

                if not validation_result.get("errors", []):
                    self.test_results["passed_tests"] += 1
                    self.test_results["test_details"].append(
                        {
                            "test": f'Admin validation for {test_case["topic"]}',
                            "status": "PASSED",
                            "validation_result": validation_result,
                        }
                    )
                    print(f"  ✅ {test_case['topic']}: Validation passed")
                else:
                    self.test_results["failed_tests"] += 1
                    self.test_results["test_details"].append(
                        {
                            "test": f'Admin validation for {test_case["topic"]}',
                            "status": "FAILED",
                            "validation_errors": validation_result.get("errors", []),
                        }
                    )
                    print(f"  ❌ {test_case['topic']}: Validation failed - {validation_result.get('errors', [])}")

            except Exception as e:
                self.test_results["failed_tests"] += 1
                self.test_results["test_details"].append(
                    {"test": f'Admin validation for {test_case["topic"]}', "status": "FAILED", "error": str(e)}
                )
                print(f"  ❌ {test_case['topic']}: {e}")

    def _test_ccu_message_validation(self):
        """Test 3: MessageManager Validation (CCU Domain)"""
        print("\n📋 Test 3: CCU MessageManager Validation")

        test_cases = [
            {"topic": "ccu/status/health", "payload": {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}},
            {"topic": "ccu/state/stock", "payload": {"items": [{"id": "ITEM-001", "quantity": 5}]}},
        ]

        for test_case in test_cases:
            self.test_results["total_tests"] += 1

            try:
                validation_result = self.ccu_message_manager.validate_message(test_case["topic"], test_case["payload"])

                if not validation_result.get("errors", []):
                    self.test_results["passed_tests"] += 1
                    self.test_results["test_details"].append(
                        {
                            "test": f'CCU validation for {test_case["topic"]}',
                            "status": "PASSED",
                            "validation_result": validation_result,
                        }
                    )
                    print(f"  ✅ {test_case['topic']}: CCU validation passed")
                else:
                    self.test_results["failed_tests"] += 1
                    self.test_results["test_details"].append(
                        {
                            "test": f'CCU validation for {test_case["topic"]}',
                            "status": "FAILED",
                            "validation_errors": validation_result.get("errors", []),
                        }
                    )
                    print(f"  ❌ {test_case['topic']}: CCU validation failed - {validation_result.get('errors', [])}")

            except Exception as e:
                self.test_results["failed_tests"] += 1
                self.test_results["test_details"].append(
                    {"test": f'CCU validation for {test_case["topic"]}', "status": "FAILED", "error": str(e)}
                )
                print(f"  ❌ {test_case['topic']}: {e}")

    def _test_payload_generator_quality(self):
        """Test 4: PayloadGenerator Quality"""
        print("\n📋 Test 4: PayloadGenerator Quality")

        # Test critical topics that were problematic before
        critical_topics = ["ccu/order/active", "ccu/order/completed", "ccu/state/config", "ccu/state/flows"]

        for topic in critical_topics:
            self.test_results["total_tests"] += 1

            try:
                payload = self.payload_generator.generate_example_payload(topic)

                if payload:
                    # Validate the generated payload
                    validation_result = self.admin_message_manager.validate_message(topic, payload)

                    if not validation_result.get("errors", []):
                        self.test_results["passed_tests"] += 1
                        self.test_results["test_details"].append(
                            {"test": f"PayloadGenerator quality for {topic}", "status": "PASSED", "payload": payload}
                        )
                        print(f"  ✅ {topic}: PayloadGenerator quality passed")
                    else:
                        self.test_results["failed_tests"] += 1
                        self.test_results["test_details"].append(
                            {
                                "test": f"PayloadGenerator quality for {topic}",
                                "status": "FAILED",
                                "validation_errors": validation_result.get("errors", []),
                            }
                        )
                        print(f"  ❌ {topic}: PayloadGenerator quality failed - {validation_result.get('errors', [])}")
                else:
                    self.test_results["failed_tests"] += 1
                    self.test_results["test_details"].append(
                        {
                            "test": f"PayloadGenerator quality for {topic}",
                            "status": "FAILED",
                            "error": "No payload generated",
                        }
                    )
                    print(f"  ❌ {topic}: No payload generated")

            except Exception as e:
                self.test_results["failed_tests"] += 1
                self.test_results["test_details"].append(
                    {"test": f"PayloadGenerator quality for {topic}", "status": "FAILED", "error": str(e)}
                )
                print(f"  ❌ {topic}: {e}")

    def _test_schema_tester_consistency(self):
        """Test 5: Schema Tester Consistency"""
        print("\n📋 Test 5: Schema Tester Consistency")

        self.test_results["total_tests"] += 1

        try:
            # Run schema test multiple times to check for consistency
            test_results_1 = self.schema_tester.run_schema_test()
            test_results_2 = self.schema_tester.run_schema_test()

            # Check if results are consistent
            if (
                test_results_1["invalid_count"] == test_results_2["invalid_count"]
                and test_results_1["valid_count"] == test_results_2["valid_count"]
            ):

                self.test_results["passed_tests"] += 1
                self.test_results["test_details"].append(
                    {
                        "test": "Schema Tester Consistency",
                        "status": "PASSED",
                        "invalid_count_1": test_results_1["invalid_count"],
                        "invalid_count_2": test_results_2["invalid_count"],
                    }
                )
                print(f"  ✅ Schema Tester: Consistent results ({test_results_1['invalid_count']} invalid)")
            else:
                self.test_results["failed_tests"] += 1
                self.test_results["test_details"].append(
                    {
                        "test": "Schema Tester Consistency",
                        "status": "FAILED",
                        "invalid_count_1": test_results_1["invalid_count"],
                        "invalid_count_2": test_results_2["invalid_count"],
                    }
                )
                print(
                    f"  ❌ Schema Tester: Inconsistent results ({test_results_1['invalid_count']} vs {test_results_2['invalid_count']})"
                )

        except Exception as e:
            self.test_results["failed_tests"] += 1
            self.test_results["test_details"].append(
                {"test": "Schema Tester Consistency", "status": "FAILED", "error": str(e)}
            )
            print(f"  ❌ Schema Tester: {e}")

    def print_summary(self):
        """Print test summary"""
        print("\n📊 TEST SUMMARY:")
        print(f"  Total Tests: {self.test_results['total_tests']}")
        print(f"  ✅ Passed: {self.test_results['passed_tests']}")
        print(f"  ❌ Failed: {self.test_results['failed_tests']}")

        success_rate = (
            (self.test_results["passed_tests"] / self.test_results["total_tests"] * 100)
            if self.test_results["total_tests"] > 0
            else 0
        )
        print(f"  📈 Success Rate: {success_rate:.1f}%")

        if self.test_results["failed_tests"] == 0:
            print("\n🎉 ALL TESTS PASSED! MessageManager Integration is ready for Task 2.9-F")
        else:
            print(f"\n⚠️ {self.test_results['failed_tests']} tests failed. Review before proceeding to Task 2.9-F")


def main():
    """Main test execution"""
    print("🚀 Task 2.9-E: Live-Modus Test (Replay Environment)")
    print("=" * 60)

    tester = MessageManagerIntegrationTester()
    results = tester.run_all_tests()
    tester.print_summary()

    # Save results to file
    results_file = project_root / "docs/07-analysis/task-2-9-e-test-results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n📄 Detailed results saved to: {results_file}")

    return results["failed_tests"] == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
