#!/usr/bin/env python3
"""
Registry v1 Manager - Einheitliche Fehlerbehandlung und Caching
Version: 1.0.0
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

from src_orbis.omf.tools.logging_config import get_logger


class RegistryError(Exception):
    """Base exception for Registry errors"""

    pass


class UnknownTopicError(RegistryError):
    """Topic not found in resolver"""

    def __init__(self, topic: str):
        self.topic = topic
        super().__init__(f"Unknown topic: {topic}")


class TemplateMissingError(RegistryError):
    """Template key not found"""

    def __init__(self, key: str, topic: str = None):
        self.key = key
        self.topic = topic
        super().__init__(f"Template missing: {key}" + (f" for topic: {topic}" if topic else ""))


class ValidationError(RegistryError):
    """Template validation errors (non-blocking)"""

    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(f"Validation errors: {', '.join(errors)}")


class Registry:
    """Registry v1 Manager mit Caching und Fehlerbehandlung"""

    def __init__(self, root: str = None, watch_mode: bool = False):
        self.logger = get_logger("omf.tools.registry")
        self.logger.info("Registry v1 Manager initialisiert")

        if root is None:
            # Projekt-Root-relative Pfade verwenden
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent.parent  # src_orbis/omf/tools -> src_orbis -> . -> Projekt-Root
            root = project_root / "registry" / "model" / "v1"

        self.root = Path(root)
        self.logger.info(f"Registry-Root: {self.root}")
        self.watch_mode = watch_mode
        self._cache = {}
        self._mtime_cache = {}

        # Version-Pinning prüfen
        self._check_version_pinning()

    def _check_version_pinning(self):
        """Version-Pinning: assert registry.manifest()["version"].startswith("1.")"""
        try:
            manifest = self.load_yaml("manifest.yml")
            version = manifest.get("version", "")
            if not version.startswith("1."):
                raise RegistryError(f"Version pinning violation: expected v1.x.x, got {version}")
            self.logger.info(f"✅ Registry version check passed: {version}")
        except Exception as e:
            self.logger.error(f"❌ Registry version check failed: {e}")
            raise

    def load_yaml(self, path: Union[str, Path]) -> Dict[str, Any]:
        """Load YAML with caching and hot-reload"""
        file_path = self.root / path if isinstance(path, str) else path

        # Check if file exists
        if not file_path.exists():
            self.logger.warning(f"⚠️ File not found: {file_path}")
            return {}

        # Check mtime for hot-reload
        current_mtime = file_path.stat().st_mtime
        cached_mtime = self._mtime_cache.get(str(file_path))

        if self.watch_mode and cached_mtime and current_mtime > cached_mtime:
            self.logger.info(f"🔄 Hot-reload: {file_path}")
            if str(file_path) in self._cache:
                del self._cache[str(file_path)]

        # Load from cache or file
        if str(file_path) not in self._cache:
            try:
                with open(file_path, encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                self._cache[str(file_path)] = data
                self._mtime_cache[str(file_path)] = current_mtime
                self.logger.debug(f"📁 Loaded: {file_path}")
            except Exception as e:
                self.logger.error(f"❌ Error loading {file_path}: {e}")
                return {}

        return self._cache[str(file_path)]

    def manifest(self) -> Dict[str, Any]:
        return self.load_yaml("manifest.yml")

    def modules(self) -> Dict[str, Any]:
        return self.load_yaml("modules.yml")

    def enums(self) -> Dict[str, Any]:
        return self.load_yaml("enums.yml")

    def workpieces(self) -> Dict[str, Any]:
        """Leere workpieces.yml: Loader liefert leeres Mapping statt Exception"""
        data = self.load_yaml("workpieces.yml")
        return data if data else {"nfc_codes": {}}

    def mapping(self) -> Dict[str, Any]:
        return self.load_yaml("mappings/topic_template.yml")

    def templates(self) -> Dict[str, Any]:
        """Load all templates from registry/model/v0/templates/"""
        templates = {}
        templates_dir = self.root / "templates"
        if templates_dir.exists():
            for template_file in templates_dir.glob("*.yml"):
                template_name = template_file.stem
                templates[template_name] = self.load_yaml(template_file)
        return templates

    def topics(self) -> Dict[str, Any]:
        """Load all topics from registry/model/v0/topics/"""
        topics = {}
        topics_dir = self.root / "topics"
        if topics_dir.exists():
            for topic_file in topics_dir.glob("*.yml"):
                topic_name = topic_file.stem
                topics[topic_name] = self.load_yaml(topic_file)
        return topics


class TopicResolver:
    """Deterministisch: exact > pattern"""

    VAR = re.compile(r"\{([a-zA-Z0-9_]+)\}")

    def __init__(self, mapping: Dict[str, Any]):
        self.logger = get_logger("omf.tools.registry")
        self.exact = [m for m in mapping.get("mappings", []) if "topic" in m]
        self.pattern = [(m, self._compile(m["pattern"])) for m in mapping.get("mappings", []) if "pattern" in m]
        self.default_dir = mapping.get("defaults", {}).get("direction", "inbound")
        self.logger.info(f"TopicResolver initialisiert: {len(self.exact)} exact, {len(self.pattern)} pattern mappings")

    def _compile(self, pat: str) -> re.Pattern:
        """Compile pattern with variable extraction"""
        try:
            # First replace variables, then escape
            rgx = self.VAR.sub(lambda m: f"(?P<{m.group(1)}>[^/]+)", pat)
            return re.compile("^" + rgx + "$")
        except re.error as e:
            self.logger.error(f"❌ Regex compilation error for pattern '{pat}': {e}")
            # Fallback: simple pattern matching
            return re.compile("^" + re.escape(pat).replace(r"\{[^}]+\}", r"[^/]+") + "$")

    def resolve(self, topic: str) -> Optional[Dict[str, Any]]:
        """Resolve topic to template mapping"""
        # Exact match first
        for m in self.exact:
            if m["topic"] == topic:
                return {
                    "template": m["template"],
                    "direction": m.get("direction", self.default_dir),
                    "vars": {},
                    "meta": m.get("meta"),
                }

        # Pattern match
        for m, rgx in self.pattern:
            mo = rgx.match(topic)
            if mo:
                return {
                    "template": m["template"],
                    "direction": m.get("direction", self.default_dir),
                    "vars": mo.groupdict(),
                    "meta": m.get("meta"),
                }

        # Unknown topic
        self.logger.warning(f"⚠️ Unknown topic: {topic}")
        return None


class TopicManager:
    """Topic routing with error handling"""

    def __init__(self, registry: Registry):
        self.logger = get_logger("omf.tools.registry")
        self.reg = registry
        self._mapping = registry.mapping()
        self._resolver = TopicResolver(self._mapping)
        self._unknown_topics = set()  # Telemetrie
        self.logger.info("TopicManager initialisiert")

    def route(self, topic: str) -> Optional[Dict[str, Any]]:
        """Route topic to template mapping with error handling"""
        result = self._resolver.resolve(topic)
        if result is None:
            self._unknown_topics.add(topic)
            self.logger.warning(f"⚠️ Unknown topic: {topic}")
        return result

    def get_unknown_topics(self) -> set:
        """Get telemetry for unknown topics"""
        return self._unknown_topics.copy()


class MessageTemplateManager:
    """Message template management with validation"""

    def __init__(self, registry: Registry):
        self.logger = get_logger("omf.tools.registry")
        self.reg = registry
        self._templates = registry.templates()
        self._missing_templates = set()  # Telemetrie
        self.logger.info("MessageTemplateManager initialisiert")

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get template by key with hierarchical fallback"""
        if key in self._templates:
            return self._templates[key]

        # Hierarchical keys "module/state.hbw_inventory" → file "module.state.hbw_inventory.yml"
        alt = key.replace("/", ".")
        if alt in self._templates:
            return self._templates[alt]

        self._missing_templates.add(key)
        self.logger.warning(f"⚠️ Template missing: {key}")
        return None

    def validate_payload(self, key: str, payload: Dict[str, Any]) -> List[str]:
        """Leichter Contract-Check: required_fields, enum-Felder, etc. (non-blocking)"""
        template = self.get(key)
        if not template:
            return [f"Template missing: {key}"]

        errors = []

        # Required fields check
        required_fields = template.get("match", {}).get("required_fields", [])
        for field in required_fields:
            if field not in payload:
                errors.append(f"missing field: {field}")

        # Enum fields check
        command_enum = template.get("match", {}).get("command_enum", [])
        if command_enum and payload.get("command") not in command_enum:
            errors.append(f"command not in enum {command_enum}")

        # Log validation errors (non-blocking)
        if errors:
            self.logger.warning(f"⚠️ Validation errors for {key}: {errors}")

        return errors

    def get_missing_templates(self) -> set:
        """Get telemetry for missing templates"""
        return self._missing_templates.copy()


# Global registry instance
_registry = None


def get_registry(watch_mode: bool = False) -> Registry:
    """Get global registry instance with optional watch mode"""
    global _registry
    if _registry is None or watch_mode != _registry.watch_mode:
        _registry = Registry(watch_mode=watch_mode)
    return _registry


def get_topic_manager() -> TopicManager:
    """Get topic manager instance"""
    return TopicManager(get_registry())


def get_message_template_manager() -> MessageTemplateManager:
    """Get message template manager instance"""
    return MessageTemplateManager(get_registry())
