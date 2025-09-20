# Decision Record: Registry-basierte Konfiguration

**Datum:** 2024-12-19  
**Status:** Accepted  
**Kontext:** Das OMF-Dashboard benötigt eine zentrale, versionierte Konfiguration für Schemas, Templates und Module-Definitionen.

---

## Entscheidung

Verwendung des **Registry-Systems** mit versionierten Konfigurationsdateien in `registry/model/v1/` für zentrale Verwaltung aller Dashboard-Konfigurationen.

```python
# Registry-Pfad
registry_path = "registry/model/v1/"

# Template-Ladung
from omf.tools.message_template_manager import get_omf_message_template_manager
template_manager = get_omf_message_template_manager()
template = template_manager.get("ccu.state.stock")

# Schema-Validierung
from omf.tools.registry_manager import get_registry
registry = get_registry()
schema = registry.get_schema("topics", "aps")
```

## Konsequenzen

### Positiv:
- **Zentrale Verwaltung:** Alle Konfigurationen an einem Ort
- **Versionierung:** Schemas und Templates versioniert
- **Dynamische Ladung:** Konfigurationen zur Laufzeit ladbar
- **Konsistenz:** Einheitliche Konfigurationsstruktur
- **Wartbarkeit:** Einfache Updates und Änderungen

### Negativ:
- **Komplexität:** Zusätzliche Abstraktionsebene
- **Abhängigkeit:** Komponenten abhängig von Registry

## Implementierung

- [x] Registry-Struktur in `registry/model/v1/`
- [x] Template-Manager für Message-Templates
- [x] Schema-Manager für Validierung
- [x] Versionierte Konfigurationsdateien
- [x] Dynamische Template-Ladung

---

*Entscheidung getroffen von: OMF-Entwicklungsteam*
