        topics = self.old_data.get("topics", {})
        analysis["total_topics"] = len(topics)

        for topic, template in topics.items():
            category = template.get("category", "Unknown")
            sub_category = template.get("sub_category", "Unknown")

            # Kategorien zählen
            if category not in analysis["categories"]:
                analysis["categories"][category] = 0
            analysis["categories"][category] += 1

            # Sub-Kategorien zählen
            if sub_category not in analysis["sub_categories"]:
                analysis["sub_categories"][sub_category] = 0
            analysis["sub_categories"][sub_category] += 1

            # Topic-Verteilung
            analysis["topic_distribution"][topic] = {
                "category": category,
                "sub_category": sub_category,
                "has_examples": bool(template.get("examples")),
                "has_validation": bool(template.get("validation_rules")),
                "has_structure": bool(template.get("template_structure")),
            }

            # Beispiele pro Topic
            examples = template.get("examples", [])
            analysis["examples_per_topic"][topic] = len(examples)

            # Validierungsregeln pro Topic
            rules = template.get("validation_rules", [])
            analysis["validation_rules_per_topic"][topic] = len(rules)

        return analysis

    def migrate_templates(self, dry_run: bool = True) -> Dict[str, Any]:
        """Migriert Templates in modulare Struktur"""
        if not self.old_data:
            return {"error": "Keine alten Daten gefunden"}

        migration_report = {
            "total_topics": 0,
            "migrated_topics": 0,
            "created_files": [],
            "errors": [],
            "dry_run": dry_run,
        }

        topics = self.old_data.get("topics", {})
        migration_report["total_topics"] = len(topics)

        # Gruppiere Topics nach Kategorie und Sub-Kategorie
        grouped_templates = {}

        for topic, template in topics.items():
            category = template.get("category", "Unknown")
            sub_category = template.get("sub_category", "Unknown")

            if category not in grouped_templates:
                grouped_templates[category] = {}

            if sub_category not in grouped_templates[category]:
                grouped_templates[category][sub_category] = {}

            grouped_templates[category][sub_category][topic] = template

        # Erstelle Template-Dateien
        for category, sub_categories in grouped_templates.items():
            for sub_category, templates in sub_categories.items():
                if dry_run:
                    print(f"📁 Würde erstellen: {category}/{sub_category}.yml ({len(templates)} Templates)")
                    migration_report["created_files"].append(f"{category}/{sub_category}.yml")
                    migration_report["migrated_topics"] += len(templates)
                else:
                    success = self._create_template_file(category, sub_category, templates)
                    if success:
                        migration_report["migrated_topics"] += len(templates)
                        migration_report["created_files"].append(f"{category}/{sub_category}.yml")
                    else:
                        migration_report["errors"].append(f"Fehler bei {category}/{sub_category}")

        return migration_report

    def _create_template_file(self, category: str, sub_category: str, templates: Dict[str, Any]) -> bool:
        """Erstellt eine Template-Datei für eine Kategorie/Sub-Kategorie"""
        try:
            # Erstelle Verzeichnis
            category_dir = self.new_templates_dir / "templates" / category.lower()
            category_dir.mkdir(parents=True, exist_ok=True)

            # Dateiname
            filename = f"{sub_category.lower().replace(' ', '_')}.yml"
            file_path = category_dir / filename

            # Template-Daten erstellen
            template_data = {
                "metadata": {
                    "version": "3.0.0",
                    "last_updated": "2025-08-29",
                    "description": f"{category} {sub_category} Templates",
                    "category": category,
                    "sub_category": sub_category,
                    "icon": self._get_icon_for_category(category, sub_category),
                },
                "templates": templates,
            }

            # Datei schreiben
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    template_data,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    indent=2,
                )

            print(f"✅ {file_path} erstellt ({len(templates)} Templates)")
            return True

        except Exception as e:
            print(f"❌ Fehler beim Erstellen von {category}/{sub_category}: {e}")
            return False

    def _get_icon_for_category(self, category: str, sub_category: str) -> str:
        """Gibt Icon für Kategorie/Sub-Kategorie zurück"""
        icons = {
            "CCU": {"Control": "🎮", "Order": "📋", "State": "📊", "Wareneingang": "📦"},
            "MODULE": {
                "Connection": "🔗",
                "Factsheet": "📄",
                "InstantAction": "⚡",
                "Order": "📋",
                "State": "📊",
                "Status": "📊",
            },
            "TXT": {
                "Control": "🎮",
                "Function Input": "🔌",
                "Function Output": "🔌",
                "General": "⚙️",
                "Input": "📥",
                "Output": "📤",
            },
            "Node-RED": {
                "Connection": "🔗",
                "Dashboard": "📊",
                "Factsheet": "📄",
                "Flows": "🔄",
                "InstantAction": "⚡",
                "Order": "📋",
                "State": "📊",
                "Status": "📊",
                "UI": "🖥️",
            },
        }

        return icons.get(category, {}).get(sub_category, "📁")

    def generate_migration_report(self) -> str:
        """Generiert einen detaillierten Migrationsbericht"""
        analysis = self.analyze_old_structure()

        report = f"""
# Template Migration Report
## Analyse der alten YAML-Struktur

**Gesamt-Topics:** {analysis.get('total_topics', 0)}

### Kategorien:
"""

        for category, count in analysis.get("categories", {}).items():
            report += f"- **{category}:** {count} Topics\n"

        report += "\n### Sub-Kategorien:\n"

        for sub_category, count in analysis.get("sub_categories", {}).items():
            report += f"- **{sub_category}:** {count} Topics\n"

        report += "\n### Template-Verteilung:\n"

        for topic, info in analysis.get("topic_distribution", {}).items():
            report += f"- **{topic}:** {info['category']} → {info['sub_category']}\n"

        return report

    def validate_migration(self) -> Dict[str, Any]:
        """Validiert die Migration"""
        validation_report = {
            "old_topics": 0,
            "new_topics": 0,
            "missing_topics": [],
            "validation_errors": [],
        }

        # Zähle alte Topics
        old_topics = set(self.old_data.get("topics", {}).keys())
        validation_report["old_topics"] = len(old_topics)

        # Zähle neue Topics (würde implementiert werden)
        # Hier würde man die neuen Template-Dateien laden und vergleichen

        return validation_report


def main():
    """Hauptfunktion für Migration"""
    print("🔧 Template Migration Tool")
    print("=" * 50)

    # Migration-Tool initialisieren
    migration_tool = TemplateMigrationTool()

    # Analyse durchführen
    print("\n📊 Analysiere alte YAML-Struktur...")
    analysis = migration_tool.analyze_old_structure()

    if not analysis:
        print("❌ Keine alten Daten gefunden!")
        return

    print(f"✅ {analysis.get('total_topics', 0)} Topics gefunden")
    print(f"✅ {len(analysis.get('categories', {}))} Kategorien")
    print(f"✅ {len(analysis.get('sub_categories', {}))} Sub-Kategorien")

    # Migrationsbericht generieren
    print("\n📋 Generiere Migrationsbericht...")
    report = migration_tool.generate_migration_report()
    print(report)

    # Dry-Run Migration
    print("\n🔄 Führe Dry-Run Migration durch...")
    migration_report = migration_tool.migrate_templates(dry_run=True)

    print(
        f"✅ {migration_report.get('migrated_topics', 0)} von "
        f"{migration_report.get('total_topics', 0)} Topics würden migriert"
    )
    print(f"✅ {len(migration_report.get('created_files', []))} Dateien würden erstellt")

    # Frage nach echter Migration
    print("\n" + "=" * 50)
    print("Führe echte Migration durch...")

    # Echte Migration durchführen
    migration_report = migration_tool.migrate_templates(dry_run=False)

    print(
        f"✅ {migration_report.get('migrated_topics', 0)} von {migration_report.get('total_topics', 0)} Topics migriert"
    )
    print(f"✅ {len(migration_report.get('created_files', []))} Dateien erstellt")

    if migration_report.get("errors"):
        print(f"❌ {len(migration_report.get('errors', []))} Fehler aufgetreten")
        for error in migration_report.get("errors", []):
            print(f"   - {error}")


if __name__ == "__main__":
    main()
