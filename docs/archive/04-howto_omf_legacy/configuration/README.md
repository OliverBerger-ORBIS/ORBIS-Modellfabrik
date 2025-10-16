# Configuration Howtos

Übersicht aller Konfigurations-Guides für das OMF-Projekt.

## Verfügbare Guides

### 1. [Registry Configuration Guide](registry-configuration-guide.md)
**Status:** ✅ Aktuell  
**Version:** 3.0.0  
**Beschreibung:** Vollständiger Guide für die Registry-basierte Architektur mit Pfad-Konstanten und Manager-Klassen.

### 2. [Module Configuration Guide](module-configuration-guide.md)
**Status:** 🔄 Legacy (wird migriert)  
**Version:** 2.0.0  
**Beschreibung:** Legacy-Guide für Modul-Konfigurationen. **Wird auf Registry umgestellt.**

### 3. [NFC Code Configuration Guide](nfc-code-configuration-guide.md)
**Status:** 🔄 Legacy (wird migriert)  
**Version:** 2.0.0  
**Beschreibung:** Legacy-Guide für NFC-Code-Konfigurationen. **Wird auf Registry umgestellt.**

### 4. [Topic Configuration Guide](topic-configuration-guide.md)
**Status:** 🔄 Legacy (wird migriert)  
**Version:** 2.0.0  
**Beschreibung:** Legacy-Guide für Topic-Konfigurationen. **Wird auf Registry umgestellt.**

## Migration Status

### ✅ Abgeschlossen
- **Workpiece-Konfiguration:** `nfc_config.yml` → `registry/model/v1/workpieces.yml`
- **Module-Konfiguration:** `module_config.yml` → `registry/model/v1/modules.yml`
- **Topic-Konfiguration:** `topic_config.yml` → `registry/model/v1/topics/`

### 🔄 In Bearbeitung
- **Topic-Message-Mapping:** `topic_message_mapping.yml` → `registry/model/v1/mappings/topic_template.yml`
- **Message-Templates:** `message_templates/` → `registry/model/v1/templates/`

### 📋 Geplant
- **Produktions-Workflows:** `production/workflows.yml` → `registry/model/v1/workflows.yml`
- **Produktkatalog:** `products/product_catalog.yml` → `registry/model/v1/products.yml`
- **Shopfloor-Layout:** `shopfloor/layout.yml` → `registry/model/v1/shopfloor.yml`

## Best Practices

### 1. Immer Registry verwenden
```python
from omf.dashboard.tools.path_constants import REGISTRY_DIR
config_path = REGISTRY_DIR / "model" / "v1" / "modules.yml"
```

### 2. Manager-Klassen verwenden
```python
from omf.tools.workpiece_manager import get_omf_workpiece_manager
manager = get_omf_workpiece_manager()
```

### 3. Pfad-Konstanten verwenden
```python
from omf.dashboard.tools.path_constants import PROJECT_ROOT, REGISTRY_DIR
# Nie: Path(__file__).parent.parent.parent
```

## Entwicklung

### Neue Konfiguration hinzufügen
1. Registry-Datei erstellen
2. Manager-Klasse implementieren
3. Tests schreiben
4. Dokumentation aktualisieren

### Legacy-Konfiguration migrieren
1. Daten analysieren
2. Registry-Format erstellen
3. Manager aktualisieren
4. Legacy-Datei entfernen

---

*Letzte Aktualisierung: 2025-09-23*
