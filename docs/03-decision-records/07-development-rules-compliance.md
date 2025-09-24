# Decision Record: Development Rules Compliance

**Datum:** 2024-12-19  
**Status:** Accepted  
**Kontext:** Das OMF-Dashboard benötigt einheitliche Entwicklungsstandards für Code-Qualität, Imports und Formatierung.

---

## Entscheidung

Befolgung der **OMF Development Rules** für alle Dashboard-Komponenten.

```python
# Import-Standards
from omf.dashboard.tools.logging_config import get_logger  # Absolute Imports für externe Module
from .aps_overview_commands import show_aps_overview_commands  # Relative Imports für Paket-interne Module

# Pfad-Standards (State-of-the-Art)
from omf.dashboard.tools.path_constants import PROJECT_ROOT, SESSIONS_DIR, CONFIG_DIR, REGISTRY_DIR
data_path = SESSIONS_DIR
config_path = CONFIG_DIR / "shopfloor" / "layout.yml"
registry_path = REGISTRY_DIR / "model" / "v1" / "modules.yml"

# Logging-Standards
logger = get_logger("omf.dashboard.component_name")
logger.info("📤 MQTT Publish: topic → payload")

# UI-Refresh Pattern
from omf.dashboard.utils.ui_refresh import request_refresh
request_refresh()  # Statt st.rerun()

# MQTT-Verbindungsstabilität (KRITISCH)
# st.success(), st.error(), st.warning() sind NICHT das Problem!
# Das Problem liegt in der Reihenfolge der Funktionsaufrufe oder anderen Änderungen
logger.info("✅ Erfolgreich gesendet")  # ✅ Korrekt für Logging
st.success("✅ Erfolgreich gesendet")  # ✅ Auch korrekt - war schon immer da
```

## Konsequenzen

### Positiv:
- **Konsistenz:** Einheitlicher Code-Stil
- **Wartbarkeit:** Vorhersagbare Struktur
- **Qualität:** Automatische Code-Formatierung
- **Kompatibilität:** Pre-commit Hooks funktionieren
- **Lesbarkeit:** Einheitliche Import-Reihenfolge

### Negativ:
- **Strenge:** Weniger Flexibilität
- **Lernkurve:** Entwickler müssen Regeln befolgen

## Implementierung

- [x] Absolute Imports für externe Module
- [x] Relative Imports für Paket-interne Module
- [x] Absolute Pfade für Data-Pfade
- [x] **Registry-Pfade mit REGISTRY_DIR verwenden**
- [x] OMF-Logging-System verwenden
- [x] UI-Refresh Pattern statt st.rerun()
- [x] **MQTT-Verbindungsstabilität: Reihenfolge der Funktionsaufrufe prüfen**
- [x] Black Formatting (120 Zeichen)
- [x] Pre-commit Hooks befolgen

## Registry-Pfad-Regeln

### ✅ Korrekt:
```python
from omf.dashboard.tools.path_constants import REGISTRY_DIR
registry_path = REGISTRY_DIR / "model" / "v1" / "modules.yml"
topics_dir = REGISTRY_DIR / "model" / "v1" / "topics"
```

### ❌ Falsch:
```python
# Fehleranfällige parent.parent Ketten
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
registry_path = project_root / "registry" / "model" / "v1" / "modules.yml"

# Hardcodierte Pfade
registry_path = "/Users/oliver/Projects/ORBIS-Modellfabrik/registry/model/v1/modules.yml"
```

## MQTT-Verbindungsstabilität (KRITISCH)

### Problem:
Das MQTT-Verbindungsproblem liegt **NICHT** in `st.success()`, `st.error()`, `st.warning()` - diese waren schon immer da und funktionierten.

### ✅ Korrekt:
```python
# st.success(), st.error() sind NICHT das Problem
def _execute_fts_command(module_id):
    try:
        gateway.send(topic="ccu/set/charge", builder=lambda: {...})
        st.success(f"✅ FTS-Befehl für {module_id} erfolgreich gesendet!")  # ✅ OK
    except Exception as e:
        st.error(f"❌ Fehler beim FTS-Befehl für {module_id}: {e}")  # ✅ OK
```

### ❌ Falsch:
```python
# Das Problem liegt in der Reihenfolge der Funktionsaufrufe
def main():
    # Falsche Reihenfolge kann MQTT-Verbindung beeinträchtigen
    setup_page_config()  # ❌ Falsche Reihenfolge
    if consume_refresh():  # ❌ Zu spät aufgerufen
        st.rerun()
```

### Regel:
- **`st.success()`, `st.error()` sind NICHT das Problem** - waren schon immer da
- **Reihenfolge der Funktionsaufrufe prüfen** - das ist das echte Problem
- **`consume_refresh()` früh in `main()` aufrufen** - vor anderen Initialisierungen

---

*Entscheidung getroffen von: OMF-Entwicklungsteam*
