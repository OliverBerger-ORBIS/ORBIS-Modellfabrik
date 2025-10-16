"""
Test for forbidden st.rerun() usage in OMF2
Prevents CURSOR from accidentally adding st.rerun() calls
"""

import os
import re
import sys
import unittest
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


class TestStRerunForbidden(unittest.TestCase):
    """Test that st.rerun() is not used in OMF2 codebase"""

    def setUp(self):
        """Setup test paths"""
        self.project_root = Path(__file__).parent.parent
        self.omf2_root = self.project_root  # omf2/ is already the project root

    def test_no_st_rerun_in_ui_components(self):
        """Test that UI components don't use st.rerun()"""
        violations = []

        # Check all UI components
        ui_path = self.omf2_root / "ui"
        if ui_path.exists():
            for py_file in ui_path.rglob("*.py"):
                violations.extend(self._check_file_for_st_rerun(py_file))

        if violations:
            self.fail(
                "🚨 FORBIDDEN st.rerun() USAGE DETECTED in UI components:\n"
                + "\n".join(f"❌ {v}" for v in violations)
                + "\n💡 SOLUTION: Use request_refresh() from omf2.ui.utils.ui_refresh instead!"
            )

    def test_ui_components_import_correctly(self):
        """Test that UI components can be imported without errors"""
        import_errors = []

        # Test key UI components
        ui_components = [
            "omf2.ui.ccu.ccu_overview.ccu_overview_tab",
            "omf2.ui.ccu.ccu_orders.ccu_orders_tab",
            "omf2.ui.ccu.ccu_process.ccu_process_tab",
            "omf2.ui.ccu.ccu_configuration.ccu_configuration_tab",
            "omf2.ui.ccu.ccu_modules.ccu_modules_tab",
        ]

        for module_path in ui_components:
            try:
                __import__(module_path)
            except ImportError as e:
                import_errors.append(f"{module_path}: {str(e)}")
            except Exception as e:
                import_errors.append(f"{module_path}: Unexpected error: {str(e)}")

        if import_errors:
            self.fail(
                "🚨 UI COMPONENT IMPORT ERRORS:\n"
                + "\n".join(f"❌ {error}" for error in import_errors)
                + "\n💡 SOLUTION: Check class names and imports in UI components!"
            )

    def test_no_st_rerun_in_main_dashboard(self):
        """Test that main dashboard doesn't use st.rerun()"""
        violations = []

        # Check main dashboard files
        main_files = [
            self.omf2_root / "omf.py",
            self.omf2_root / "ui" / "main_dashboard.py",
            self.omf2_root / "ui" / "user_manager.py",
        ]

        for file_path in main_files:
            if file_path.exists():
                violations.extend(self._check_file_for_st_rerun(file_path))

        if violations:
            self.fail(
                "🚨 FORBIDDEN st.rerun() USAGE DETECTED in main dashboard:\n"
                + "\n".join(f"❌ {v}" for v in violations)
                + "\n💡 SOLUTION: Use request_refresh() from omf2.ui.utils.ui_refresh instead!"
            )

    def test_only_consume_refresh_in_main(self):
        """Test that only consume_refresh() is used in main application"""
        main_file = self.omf2_root / "omf.py"
        if not main_file.exists():
            self.skipTest("Main file not found")

        violations = []
        with open(main_file, encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")

        # Check for forbidden st.rerun() usage (except after consume_refresh())
        forbidden_patterns = [
            r"st\.rerun\s*\(",
            r"streamlit\.rerun\s*\(",
        ]

        for i, line in enumerate(lines, 1):
            # Skip comment lines and lines after consume_refresh() call
            if line.strip().startswith("#") or (i > 1 and "consume_refresh()" in lines[i - 2]):
                continue

            for pattern in forbidden_patterns:
                if re.search(pattern, line):
                    violations.append(f"{main_file}:{i}: {line.strip()}")

        if violations:
            self.fail(
                "🚨 FORBIDDEN st.rerun() USAGE DETECTED in main application:\n"
                + "\n".join(f"❌ {v}" for v in violations)
                + "\n💡 SOLUTION: Only consume_refresh() is allowed in main application!"
            )

    def test_request_refresh_imported_correctly(self):
        """Test that request_refresh() is imported correctly"""
        violations = []

        # Check files that should use request_refresh()
        files_to_check = [self.omf2_root / "ui" / "main_dashboard.py", self.omf2_root / "ui" / "user_manager.py"]

        for file_path in files_to_check:
            if file_path.exists():
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                # Check if request_refresh is imported
                if (
                    "request_refresh" in content
                    and "from omf2.ui.utils.ui_refresh import request_refresh" not in content
                ):
                    violations.append(f"{file_path}: request_refresh() used but not imported correctly")

        if violations:
            self.fail(
                "🚨 INCORRECT request_refresh() IMPORT:\n"
                + "\n".join(f"❌ {v}" for v in violations)
                + "\n💡 SOLUTION: Import with 'from omf2.ui.utils.ui_refresh import request_refresh'"
            )

    def _check_file_for_st_rerun(self, file_path: Path) -> list[str]:
        """Check a single file for forbidden st.rerun() usage."""
        violations = []

        try:
            # Skip ui_refresh.py (it's the controller for st.rerun())
            if file_path.name == "ui_refresh.py":
                return violations

            # Skip old files
            if "_old" in file_path.name or "_new" in file_path.name:
                return violations

            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

            # Check for forbidden patterns
            forbidden_patterns = [
                r"st\.rerun\s*\(",
                r"streamlit\.rerun\s*\(",
                r"\.rerun\s*\(",
            ]

            for i, line in enumerate(lines, 1):
                # Skip comment lines
                if line.strip().startswith("#"):
                    continue

                # Special handling for omf.py - allow st.rerun() after consume_refresh()
                if file_path.name == "omf.py" and i > 1 and "consume_refresh()" in lines[i - 2]:
                    continue

                for pattern in forbidden_patterns:
                    if re.search(pattern, line):
                        violations.append(f"{file_path}:{i}: {line.strip()}")

        except Exception as e:
            violations.append(f"{file_path}: Error reading file: {e}")

        return violations


class TestUIRefreshStrategy(unittest.TestCase):
    """Test UI-Refresh-Strategy implementation"""

    def test_ui_refresh_utils_exist(self):
        """Test that UI-Refresh-Utils exist"""
        ui_refresh_file = Path(__file__).parent.parent / "ui" / "utils" / "ui_refresh.py"
        self.assertTrue(ui_refresh_file.exists(), "ui_refresh.py should exist")

    def test_request_refresh_function_exists(self):
        """Test that request_refresh() function exists"""
        try:
            from omf2.ui.utils.ui_refresh import consume_refresh, request_refresh

            self.assertTrue(callable(request_refresh), "request_refresh should be callable")
            self.assertTrue(callable(consume_refresh), "consume_refresh should be callable")
        except ImportError as e:
            self.fail(f"UI-Refresh-Utils not found: {e}")

    def test_ui_refresh_strategy_documented(self):
        """Test that UI-Refresh-Strategy is documented"""
        # Check if strategy is mentioned in documentation
        readme_file = Path(__file__).parent.parent / "README.md"
        if readme_file.exists():
            with open(readme_file, encoding="utf-8") as f:
                content = f.read()
                self.assertIn("request_refresh", content, "UI-Refresh-Strategy should be documented in README")


if __name__ == "__main__":
    unittest.main()
