# Decision Record: Development Rules Compliance

**Datum:** 2024-12-19  
**Status:** Accepted  
**Kontext:** Das OMF-Dashboard benötigt einheitliche Entwicklungsstandards für Code-Qualität, Imports und Formatierung.

---

## Entscheidung

Befolgung der **OMF Development Rules** für alle Dashboard-Komponenten.

```python
# Import-Standards
from omf.tools.logging_config import get_logger  # Absolute Imports für externe Module
from .aps_overview_commands import show_aps_overview_commands  # Relative Imports für Paket-interne Module

# Pfad-Standards
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
data_path = project_root / "data/omf-data/sessions"

# Logging-Standards
logger = get_logger("omf.dashboard.component_name")
logger.info("📤 MQTT Publish: topic → payload")

# UI-Refresh Pattern
from omf.dashboard.utils.ui_refresh import request_refresh
request_refresh()  # Statt st.rerun()
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
- [x] OMF-Logging-System verwenden
- [x] UI-Refresh Pattern statt st.rerun()
- [x] Black Formatting (120 Zeichen)
- [x] Pre-commit Hooks befolgen

---

*Entscheidung getroffen von: OMF-Entwicklungsteam*
