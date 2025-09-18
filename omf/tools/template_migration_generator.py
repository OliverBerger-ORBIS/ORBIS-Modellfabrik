#!/usr/bin/env python3
"""
Template Migration Tool - Migration von alter YAML zu modularer Struktur
Version: 3.0.0
"""

from pathlib import Path
from typing import Any, Dict

import yaml

class TemplateMigrationTool:
    """Tool zur Migration der alten Template-YAML in modulare Struktur"""

    def __init__(self, old_yaml_path: str = None, new_templates_dir: str = None):
        """Initialisiert das Migration-Tool"""
        if old_yaml_path is None:
            old_yaml_path = str(Path(__file__).parent.parent.parent / "mqtt" / "config" / "message_templates.yml")

        if new_templates_dir is None:
            new_templates_dir = str(Path(__file__).parent.parent / "config" / "message_templates")

        self.old_yaml_path = Path(old_yaml_path)
        self.new_templates_dir = Path(new_templates_dir)
        self.old_data = self._load_old_yaml()

    def _load_old_yaml(self) -> Dict[str, Any]:
        """Lädt die alte YAML-Datei"""
        try:
            if self.old_yaml_path.exists():
                with open(self.old_yaml_path, encoding="utf-8") as f:
                    return yaml.safe_load(f)
            else:
                print(f"⚠️ Alte YAML-Datei nicht gefunden: {self.old_yaml_path}")
                return {}
        except Exception as e:
            print(f"❌ Fehler beim Laden der alten YAML: {e}")
            return {}

    def analyze_old_structure(self) -> Dict[str, Any]:
        """Analysiert die Struktur der alten YAML"""
        if not self.old_data:
            return {}

        # ...existing code...
