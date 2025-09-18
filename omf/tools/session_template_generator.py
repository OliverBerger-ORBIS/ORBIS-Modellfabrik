from omf.tools.logging_config import get_logger
#!/usr/bin/env python3
"""
Session Template Generator - Generiert Templates aus Session-Analyse
Version: 1.0.0
"""

import json
import logging
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml

logger = get_logger(__name__)

class SessionTemplateGenerator:
    """Generiert Message-Templates aus Session-Analyse"""

    def __init__(self, observations_dir: str = None, registry_dir: str = None):
        if observations_dir is None:
            observations_dir = "/Users/oliver/Projects/ORBIS-Modellfabrik/data/observations"
        if registry_dir is None:
            registry_dir = "/Users/oliver/Projects/ORBIS-Modellfabrik/registry/model/v0"

        self.observations_dir = Path(observations_dir)
        self.registry_dir = Path(registry_dir)
        self.templates_dir = self.registry_dir / "templates"

        # Ensure directories exist
        self.observations_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

    def analyze_session(self, session_file: Path) -> Dict[str, Any]:
        """Analysiert eine Session-Datei und extrahiert Message-Patterns"""
        logger.info(f"🔍 Analysiere Session: {session_file}")

        try:
            with open(session_file, encoding='utf-8') as f:
                session_data = json.load(f)

            # Extrahiere alle Topics und deren Payloads
            topic_patterns = defaultdict(list)
            topic_counts = Counter()

            for message in session_data.get('messages', []):
                topic = message.get('topic', '')
                payload = message.get('payload', {})

                if topic and payload:
                    topic_patterns[topic].append(payload)
                    topic_counts[topic] += 1

            # Generiere Template-Kandidaten
            template_candidates = {}
            for topic, payloads in topic_patterns.items():
                if len(payloads) > 0:
                    template_candidate = self._generate_template_candidate(topic, payloads)
                    if template_candidate:
                        template_candidates[topic] = template_candidate

            logger.info(
                f"✅ Session analysiert: {len(topic_patterns)} Topics, {len(template_candidates)} Template-Kandidaten"
            )

            return {
                'session_file': str(session_file),
                'topic_patterns': dict(topic_patterns),
                'topic_counts': dict(topic_counts),
                'template_candidates': template_candidates,
                'total_messages': len(session_data.get('messages', [])),
            }

        except Exception as e:
            logger.error(f"❌ Fehler beim Analysieren der Session {session_file}: {e}")
            return {}

    def _generate_template_candidate(self, topic: str, payloads: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Generiert einen Template-Kandidaten aus Payloads"""
        if not payloads:
            return None

        # Analysiere gemeinsame Felder
        all_fields = set()
        field_types = defaultdict(set)
        field_values = defaultdict(set)

        for payload in payloads:
            self._analyze_payload(payload, all_fields, field_types, field_values)

        # Generiere Template-Struktur
        template = {
            'version': '1.0.0',
            'topic': topic,
            'generated_from': 'session_analysis',
            'match': {
                'required_fields': list(all_fields),
                'field_types': {k: list(v) for k, v in field_types.items()},
                'sample_values': {k: list(v)[:5] for k, v in field_values.items()},  # Erste 5 Werte
            },
            'examples': payloads[:3],  # Erste 3 Beispiele
            'statistics': {
                'total_samples': len(payloads),
                'unique_fields': len(all_fields),
                'field_frequency': {field: len([p for p in payloads if field in p]) for field in all_fields},
            },
        }

        return template

    def _analyze_payload(
        self,
        payload: Dict[str, Any],
        all_fields: Set[str],
        field_types: Dict[str, Set[str]],
        field_values: Dict[str, Set[str]],
        prefix: str = "",
    ):
        """Rekursive Analyse eines Payloads"""
        for key, value in payload.items():
            field_name = f"{prefix}.{key}" if prefix else key
            all_fields.add(field_name)

            # Typ-Analyse
            value_type = type(value).__name__
            field_types[field_name].add(value_type)

            # Wert-Analyse (nur für primitive Typen)
            if isinstance(value, (str, int, float, bool)):
                field_values[field_name].add(str(value))
            elif isinstance(value, dict):
                self._analyze_payload(value, all_fields, field_types, field_values, field_name)
            elif isinstance(value, list):
                field_types[field_name].add('list')
                for item in value[:3]:  # Erste 3 Listenelemente
                    if isinstance(item, (str, int, float, bool)):
                        field_values[field_name].add(str(item))

    def generate_templates_from_sessions(self, session_dir: Path = None) -> Dict[str, Any]:
        """Generiert Templates aus allen Sessions in einem Verzeichnis"""
        if session_dir is None:
            session_dir = Path("/Users/oliver/Projects/ORBIS-Modellfabrik/data/omf-data/sessions")

        logger.info(f"🔍 Analysiere alle Sessions in: {session_dir}")

        # Finde alle Session-Dateien
        session_files = list(session_dir.glob("*.json"))
        if not session_files:
            logger.warning(f"⚠️ Keine Session-Dateien gefunden in: {session_dir}")
            return {}

        # Analysiere alle Sessions
        all_analyses = {}
        topic_aggregation = defaultdict(list)

        for session_file in session_files:
            analysis = self.analyze_session(session_file)
            if analysis:
                all_analyses[session_file.name] = analysis

                # Aggregiere Topics über alle Sessions
                for topic, payloads in analysis.get('topic_patterns', {}).items():
                    topic_aggregation[topic].extend(payloads)

        # Generiere finale Templates
        final_templates = {}
        for topic, all_payloads in topic_aggregation.items():
            template = self._generate_template_candidate(topic, all_payloads)
            if template:
                final_templates[topic] = template

        # Speichere Templates
        self._save_templates(final_templates)

        logger.info(f"✅ Template-Generierung abgeschlossen: {len(final_templates)} Templates generiert")

        return {
            'sessions_analyzed': len(all_analyses),
            'templates_generated': len(final_templates),
            'templates': final_templates,
            'analyses': all_analyses,
        }

    def _save_templates(self, templates: Dict[str, Any]):
        """Speichert generierte Templates in Registry v1 Format"""
        for topic, template in templates.items():
            # Konvertiere Topic zu Dateiname
            filename = self._topic_to_filename(topic)
            template_file = self.templates_dir / f"{filename}.yml"

            try:
                with open(template_file, 'w', encoding='utf-8') as f:
                    yaml.dump(template, f, default_flow_style=False, allow_unicode=True)
                logger.info(f"💾 Template gespeichert: {template_file}")
            except Exception as e:
                logger.error(f"❌ Fehler beim Speichern von {template_file}: {e}")

    def _topic_to_filename(self, topic: str) -> str:
        """Konvertiert Topic zu Dateiname"""
        # Ersetze Sonderzeichen
        filename = topic.replace('/', '.').replace(':', '_').replace(' ', '_')
        # Entferne führende Punkte
        filename = filename.lstrip('.')
        return filename

    def copy_templates_to_registry(self, source_dir: Path = None):
        """Kopiert generierte Templates von data/observations nach registry/"""
        if source_dir is None:
            source_dir = self.observations_dir / "generated_templates"

        if not source_dir.exists():
            logger.warning(f"⚠️ Quellverzeichnis existiert nicht: {source_dir}")
            return

        # Kopiere alle .yml Dateien
        for template_file in source_dir.glob("*.yml"):
            dest_file = self.templates_dir / template_file.name
            try:
                # Kopiere Datei
                dest_file.write_text(template_file.read_text(encoding='utf-8'), encoding='utf-8')
                logger.info(f"📋 Template kopiert: {template_file.name}")
            except Exception as e:
                logger.error(f"❌ Fehler beim Kopieren von {template_file.name}: {e}")

def main():
    """CLI für Template-Generierung"""
    import argparse

    parser = argparse.ArgumentParser(description="Session Template Generator")
    parser.add_argument("--session-dir", help="Session-Verzeichnis")
    parser.add_argument("--observations-dir", help="Observations-Verzeichnis")
    parser.add_argument("--registry-dir", help="Registry-Verzeichnis")
    parser.add_argument("--copy-templates", action="store_true", help="Templates nach Registry kopieren")

    args = parser.parse_args()

    # Logger konfigurieren
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # Generator initialisieren
    generator = SessionTemplateGenerator(observations_dir=args.observations_dir, registry_dir=args.registry_dir)

    # Templates generieren
    if args.session_dir:
        session_dir = Path(args.session_dir)
        result = generator.generate_templates_from_sessions(session_dir)
        print(f"✅ {result['templates_generated']} Templates aus {result['sessions_analyzed']} Sessions generiert")

    # Templates kopieren
    if args.copy_templates:
        generator.copy_templates_to_registry()

if __name__ == "__main__":
    main()
