"""
Template Analyse Komponente
Analyse aller APS-Sessions mit Fokus auf bestimmte Topics
"""

import logging
from pathlib import Path
from typing import Any, Dict

import streamlit as st

from src_orbis.analysis_tools.template_analyzers.ccu_template_analyzer import CCUTemplateAnalyzer

# Import bestehende Template-Analyser
from src_orbis.analysis_tools.template_analyzers.module_template_analyzer import ModuleTemplateAnalyzer
from src_orbis.analysis_tools.template_analyzers.nodered_template_analyzer import NodeRedTemplateAnalyzer
from src_orbis.analysis_tools.template_analyzers.txt_template_analyzer import TXTTemplateAnalyzer

logger = logging.getLogger(__name__)


def show_template_analysis():
    """Template Analyse Tab"""
    logger.info("🔍 Template Analysis Tab geladen")

    st.header("🔍 Template Analyse")
    st.markdown("Analyse aller APS-Sessions mit Fokus auf bestimmte Topics")

    # Session-Verzeichnis aus Settings
    settings_manager = st.session_state.get("settings_manager")
    if settings_manager and hasattr(settings_manager, 'session_analysis'):
        session_dir = settings_manager.session_analysis.get("session_directory", "data/omf-data/sessions")
    else:
        session_dir = "data/omf-data/sessions"
    session_path = Path(session_dir)

    if not session_path.exists():
        st.error(f"❌ Session-Verzeichnis nicht gefunden: {session_path}")
        return

    # Template-Analyzer Auswahl
    st.subheader("📋 Template-Analyzer")

    analyzer_type = st.selectbox(
        "Analyser-Typ auswählen:",
        ["🏭 Module Templates", "🎛️ CCU Templates", "📱 TXT Templates", "🔄 Node-RED Templates", "📊 Alle Analyser"],
    )

    if st.button("🔍 Template-Analyse starten", key="start_template_analysis"):
        with st.spinner("Analysiere Sessions..."):
            results = run_template_analysis(analyzer_type, session_path)
            display_analysis_results(results)

    # Observations-Templates Übersicht
    st.subheader("📁 Observations-Templates")
    display_observations_templates()


def run_template_analysis(analyzer_type: str, session_path: Path) -> Dict[str, Any]:
    """Führt Template-Analyse mit den bestehenden Analysern durch"""
    results = {
        "analyzer_type": analyzer_type,
        "session_path": str(session_path),
        "templates_generated": 0,
        "errors": [],
        "templates": {},
    }

    try:
        if analyzer_type == "🏭 Module Templates" or analyzer_type == "📊 Alle Analyser":
            logger.info("🔍 Starte Module Template Analyse")
            module_analyzer = ModuleTemplateAnalyzer(str(session_path))
            module_results = module_analyzer.analyze_all_sessions()
            results["templates"]["module"] = module_results
            results["templates_generated"] += len(module_results.get("templates", {}))

        if analyzer_type == "🎛️ CCU Templates" or analyzer_type == "📊 Alle Analyser":
            logger.info("🔍 Starte CCU Template Analyse")
            ccu_analyzer = CCUTemplateAnalyzer()
            ccu_results = ccu_analyzer.analyze_all_sessions()
            results["templates"]["ccu"] = ccu_results
            results["templates_generated"] += len(ccu_results.get("templates", {}))

        if analyzer_type == "📱 TXT Templates" or analyzer_type == "📊 Alle Analyser":
            logger.info("🔍 Starte TXT Template Analyse")
            txt_analyzer = TXTTemplateAnalyzer()
            txt_results = txt_analyzer.analyze_all_sessions()
            results["templates"]["txt"] = txt_results
            results["templates_generated"] += len(txt_results.get("templates", {}))

        if analyzer_type == "🔄 Node-RED Templates" or analyzer_type == "📊 Alle Analyser":
            logger.info("🔍 Starte Node-RED Template Analyse")
            nodered_analyzer = NodeRedTemplateAnalyzer()
            nodered_results = nodered_analyzer.analyze_all_sessions()
            results["templates"]["nodered"] = nodered_results
            results["templates_generated"] += len(nodered_results.get("templates", {}))

    except Exception as e:
        logger.error(f"❌ Fehler bei Template-Analyse: {e}")
        results["errors"].append(str(e))

    return results


def display_analysis_results(results: Dict[str, Any]):
    """Zeigt die Analyse-Ergebnisse an"""
    st.success(f"✅ Template-Analyse abgeschlossen: {results['templates_generated']} Templates generiert")

    if results["errors"]:
        st.error("❌ Fehler aufgetreten:")
        for error in results["errors"]:
            st.error(f"- {error}")

    # Zeige Templates nach Kategorie
    for category, templates in results["templates"].items():
        if templates:
            with st.expander(f"📋 {category.upper()} Templates ({len(templates.get('templates', {}))})"):
                display_category_templates(templates)


def display_category_templates(templates: Dict[str, Any]):
    """Zeigt Templates einer Kategorie an"""
    template_data = templates.get("templates", {})

    if not template_data:
        st.info("Keine Templates gefunden")
        return

    # Template-Auswahl
    selected_template = st.selectbox(
        "Template auswählen:", list(template_data.keys()), key=f"template_select_{id(templates)}"
    )

    if selected_template:
        template_info = template_data[selected_template]

        # Template-Informationen
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Nachrichten analysiert", template_info.get("message_count", 0))
            st.metric("Eindeutige Felder", template_info.get("unique_fields", 0))

        with col2:
            st.metric("Häufigstes Pattern", template_info.get("most_common_pattern", "N/A"))
            st.metric("Durchschnittliche Größe", f"{template_info.get('avg_size', 0)} bytes")

        # Template-Struktur
        st.subheader("📋 Template-Struktur")
        if "template_structure" in template_info:
            st.json(template_info["template_structure"])

        # Beispiele
        st.subheader("📝 Beispiele")
        if "examples" in template_info:
            for i, example in enumerate(template_info["examples"][:3]):  # Erste 3 Beispiele
                with st.expander(f"Beispiel {i+1}"):
                    st.json(example)

        # Export-Button
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📤 Template nach Observations exportieren", key=f"export_{selected_template}"):
                copy_template_to_observations(selected_template, template_info)

        with col2:
            if st.button("🔄 Alle Observations nach Registry kopieren", key="copy_all_to_registry"):
                copy_observations_to_registry()


def copy_template_to_observations(template_name: str, template_info: Dict[str, Any]):
    """Exportiert Template nach data/observations/"""
    try:
        # Projekt-Root-relative Pfade verwenden
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent.parent.parent.parent.parent

        # Observations Templates-Verzeichnis
        observations_templates_dir = project_root / "data" / "observations" / "generated_templates"
        observations_templates_dir.mkdir(parents=True, exist_ok=True)

        # Template-Datei erstellen
        template_file = observations_templates_dir / f"{template_name}.yml"

        # Template-Struktur für Observations formatieren
        observations_template = {
            "version": "1.0.0",
            "generated_from": "session_analysis",
            "generated_at": str(Path(__file__).stat().st_mtime),
            "match": template_info.get("template_structure", {}),
            "examples": template_info.get("examples", [])[:3],
            "statistics": {
                "message_count": template_info.get("message_count", 0),
                "unique_fields": template_info.get("unique_fields", 0),
                "avg_size": template_info.get("avg_size", 0),
            },
            "export_note": "Template wurde von Session-Analyse generiert. Manuell nach registry/model/v1/templates/ kopieren.",
        }

        # YAML speichern
        import yaml

        with open(template_file, 'w', encoding='utf-8') as f:
            yaml.dump(observations_template, f, default_flow_style=False, allow_unicode=True)

        st.success(f"✅ Template exportiert nach: {template_file}")
        st.info(
            "💡 **Hinweis:** Template wurde nach `data/observations/generated_templates/` exportiert. Manuell nach `registry/model/v1/templates/` kopieren."
        )
        logger.info(f"Template {template_name} nach Observations exportiert: {template_file}")

    except Exception as e:
        st.error(f"❌ Fehler beim Export: {e}")
        logger.error(f"Fehler beim Export von Template {template_name}: {e}")


def copy_observations_to_registry():
    """Kopiert alle Templates von data/observations nach registry/"""
    try:
        # Projekt-Root-relative Pfade verwenden
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent.parent.parent.parent.parent

        # Quell- und Ziel-Verzeichnisse
        source_dir = project_root / "data" / "observations" / "generated_templates"
        target_dir = project_root / "registry" / "model" / "v1" / "templates"

        if not source_dir.exists():
            st.error(f"❌ Quellverzeichnis nicht gefunden: {source_dir}")
            return

        target_dir.mkdir(parents=True, exist_ok=True)

        # Kopiere alle .yml Dateien
        copied_count = 0
        for template_file in source_dir.glob("*.yml"):
            dest_file = target_dir / template_file.name
            dest_file.write_text(template_file.read_text(encoding='utf-8'), encoding='utf-8')
            copied_count += 1

        st.success(f"✅ {copied_count} Templates von Observations nach Registry kopiert")
        logger.info(f"{copied_count} Templates von {source_dir} nach {target_dir} kopiert")

    except Exception as e:
        st.error(f"❌ Fehler beim Kopieren: {e}")
        logger.error(f"Fehler beim Kopieren von Observations nach Registry: {e}")


def display_observations_templates():
    """Zeigt eine Übersicht der Observations-Templates"""
    try:
        # Projekt-Root-relative Pfade verwenden
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent.parent.parent.parent.parent

        # Observations Templates-Verzeichnis
        observations_dir = project_root / "data" / "observations" / "generated_templates"

        if not observations_dir.exists():
            st.info("📁 Keine Observations-Templates gefunden. Führen Sie zuerst eine Template-Analyse durch.")
            return

        # Liste alle Template-Dateien
        template_files = list(observations_dir.glob("*.yml"))

        if not template_files:
            st.info("📁 Keine Template-Dateien in Observations gefunden.")
            return

        st.success(f"📁 {len(template_files)} Templates in Observations gefunden")

        # Template-Liste anzeigen
        for template_file in template_files:
            with st.expander(f"📄 {template_file.name}"):
                try:
                    import yaml

                    with open(template_file, encoding='utf-8') as f:
                        template_data = yaml.safe_load(f)

                    # Template-Informationen anzeigen
                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric("Version", template_data.get("version", "N/A"))
                        st.metric("Generiert von", template_data.get("generated_from", "N/A"))

                    with col2:
                        stats = template_data.get("statistics", {})
                        st.metric("Nachrichten", stats.get("message_count", 0))
                        st.metric("Eindeutige Felder", stats.get("unique_fields", 0))

                    # Export-Note
                    if "export_note" in template_data:
                        st.info(f"💡 {template_data['export_note']}")

                except Exception as e:
                    st.error(f"❌ Fehler beim Laden von {template_file.name}: {e}")

        # Bulk-Export-Button
        if st.button("🔄 Alle Observations nach Registry kopieren", key="bulk_copy_to_registry"):
            copy_observations_to_registry()

    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Observations-Templates: {e}")
        logger.error(f"Fehler beim Laden der Observations-Templates: {e}")
