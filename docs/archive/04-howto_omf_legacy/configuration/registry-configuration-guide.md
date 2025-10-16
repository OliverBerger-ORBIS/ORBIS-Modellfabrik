# Registry Configuration Guide

**Version:** 3.0.0  
**Letzte Aktualisierung:** 2025-09-23  
**Status:** Registry-basierte Architektur

## Übersicht

Das OMF-Projekt verwendet eine **Registry-basierte Architektur** als zentrale Datenquelle für alle Konfigurationen. Alle Legacy-Konfigurationen wurden auf die Registry migriert.

## Registry-Struktur

```
registry/
└── model/
    └── v1/
        ├── modules.yml          # Modul-Konfigurationen
        ├── workpieces.yml       # Werkstück-Konfigurationen
        ├── mapping.yml          # Topic-Template-Mappings
        ├── topics/              # Topic-Konfigurationen
        │   ├── ccu.yml
        │   ├── module.yml
        │   ├── txt.yml
        │   ├── nodered.yml
        │   ├── fts.yml
        │   └── aps.yml
        ├── templates/           # Message-Templates
        │   ├── ccu/
        │   ├── module/
        │   ├── txt/
        │   └── nodered/
        └── mappings/
            └── topic_template.yml
```

## Pfad-Konstanten verwenden

### ✅ Korrekte Verwendung

```python
from omf.dashboard.tools.path_constants import REGISTRY_DIR, PROJECT_ROOT

# Registry-Zugriffe
modules_path = REGISTRY_DIR / "model" / "v1" / "modules.yml"
workpieces_path = REGISTRY_DIR / "model" / "v1" / "workpieces.yml"
topics_dir = REGISTRY_DIR / "model" / "v1" / "topics"
templates_dir = REGISTRY_DIR / "model" / "v1" / "templates"

# Projekt-Root-Zugriffe
data_dir = PROJECT_ROOT / "data"
config_dir = PROJECT_ROOT / "omf" / "config"
```

### ❌ Falsche Verwendung

```python
# Fehleranfällige parent.parent Ketten
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
registry_path = project_root / "registry" / "model" / "v1" / "modules.yml"

# Hardcodierte Pfade
registry_path = "/Users/oliver/Projects/ORBIS-Modellfabrik/registry/model/v1/modules.yml"

# Relative Pfade
registry_path = "../../../registry/model/v1/modules.yml"
```

## Manager-Klassen

### OmfWorkpieceManager

```python
from omf.tools.workpiece_manager import get_omf_workpiece_manager

# Manager initialisieren
workpiece_manager = get_omf_workpiece_manager()

# Werkstücke abrufen
all_workpieces = workpiece_manager.get_all_workpieces()
red_workpieces = workpiece_manager.get_workpieces_by_color("RED")
workpiece_info = workpiece_manager.get_workpiece_info("040a8dca341291")
```

### OmfModuleManager

```python
from omf.tools.module_manager import OmfModuleManager

# Manager initialisieren
module_manager = OmfModuleManager()

# Module abrufen
all_modules = module_manager.get_all_modules()
module_info = module_manager.get_module_info("SVR3QA0022")
modules_by_type = module_manager.get_modules_by_type("Storage")
```

### OmfTopicManager

```python
from omf.tools.topic_manager import OmfTopicManager

# Manager initialisieren
topic_manager = OmfTopicManager()

# Topics abrufen
all_topics = topic_manager.get_all_topics()
friendly_name = topic_manager.get_friendly_name("ccu/state")
topic_info = topic_manager.get_topic_info("ccu/state")
```

## Migration von Legacy-Konfigurationen

### Abgeschlossene Migrationen

- ✅ **nfc_config.yml** → **workpieces.yml**
- ✅ **module_config.yml** → **modules.yml**
- ✅ **topic_config.yml** → **topics/**

### Verbleibende Legacy-Konfigurationen

- 🔄 **topic_message_mapping.yml** → **mappings/topic_template.yml**
- 🔄 **message_templates/** → **templates/**

## Best Practices

### 1. Immer Pfad-Konstanten verwenden

```python
# ✅ Korrekt
from omf.dashboard.tools.path_constants import REGISTRY_DIR
config_path = REGISTRY_DIR / "model" / "v1" / "modules.yml"

# ❌ Falsch
config_path = Path(__file__).parent.parent.parent / "registry" / "model" / "v1" / "modules.yml"
```

### 2. Manager-Klassen verwenden

```python
# ✅ Korrekt
from omf.tools.workpiece_manager import get_omf_workpiece_manager
manager = get_omf_workpiece_manager()
workpieces = manager.get_all_workpieces()

# ❌ Falsch
import yaml
with open("registry/model/v1/workpieces.yml") as f:
    workpieces = yaml.safe_load(f)
```

### 3. Fehlerbehandlung

```python
try:
    manager = OmfModuleManager()
    modules = manager.get_all_modules()
except ValueError as e:
    logger.error(f"Fehler beim Laden der Module: {e}")
    # Fallback-Logik
```

### 4. Logging verwenden

```python
from omf.dashboard.tools.logging_config import get_logger

logger = get_logger("omf.tools.module_manager")
logger.info("✅ Module erfolgreich geladen")
logger.warning("⚠️ Legacy-Konfiguration verwendet")
logger.error("❌ Registry nicht gefunden")
```

## Troubleshooting

### Problem: Registry nicht gefunden

```python
# Debug-Informationen
from omf.dashboard.tools.path_constants import get_path_info
print(get_path_info())
```

### Problem: Manager lädt nicht

```python
# Pfad-Validierung
from omf.dashboard.tools.path_constants import validate_paths
try:
    validate_paths()
    print("✅ Alle Pfade validiert")
except FileNotFoundError as e:
    print(f"❌ Fehlende Verzeichnisse: {e}")
```

### Problem: Legacy-Fallback aktiv

```python
# Prüfen, ob Registry verwendet wird
manager = OmfWorkpieceManager()
if manager.is_using_registry():
    print("✅ Registry wird verwendet")
else:
    print("⚠️ Legacy-Konfiguration wird verwendet")
```

## Entwicklung

### Neue Konfiguration hinzufügen

1. **Registry-Datei erstellen:**
   ```bash
   touch registry/model/v1/neue_konfiguration.yml
   ```

2. **Manager-Klasse erstellen:**
   ```python
   from omf.dashboard.tools.path_constants import REGISTRY_DIR
   
   class OmfNeueKonfigurationManager:
       def __init__(self):
           self.config_path = REGISTRY_DIR / "model" / "v1" / "neue_konfiguration.yml"
   ```

3. **Tests erstellen:**
   ```python
   def test_neue_konfiguration_manager():
       manager = OmfNeueKonfigurationManager()
       assert manager.load_config() is not None
   ```

### Legacy-Konfiguration migrieren

1. **Daten analysieren:**
   ```python
   # Legacy-Daten lesen
   with open("omf/config/legacy_config.yml") as f:
       legacy_data = yaml.safe_load(f)
   ```

2. **Registry-Format erstellen:**
   ```yaml
   # registry/model/v1/neue_konfiguration.yml
   metadata:
     version: "3.0.0"
     source: "omf/config/legacy_config.yml"
   
   data:
     # Migrierte Daten hier
   ```

3. **Manager aktualisieren:**
   ```python
   # Registry als primäre Quelle
   registry_path = REGISTRY_DIR / "model" / "v1" / "neue_konfiguration.yml"
   ```

4. **Legacy-Datei entfernen:**
   ```bash
   rm omf/config/legacy_config.yml
   ```

---

*Guide erstellt von: OMF-Entwicklungsteam*  
*Letzte Aktualisierung: 2025-09-23*
