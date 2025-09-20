# Decision Record: UI-Refresh Pattern

**Datum:** 2024-12-19  
**Status:** Accepted  
**Kontext:** Das OMF-Dashboard benötigt ein thread-sicheres UI-Update-System, das Endlosschleifen vermeidet und konsistente Updates gewährleistet.

---

## Entscheidung

Verwendung des **UI-Refresh Pattern** mit `request_refresh()` statt `st.rerun()` für thread-sichere UI-Updates.

```python
# UI-Refresh Pattern
from omf.dashboard.utils.ui_refresh import request_refresh

# Statt st.rerun() verwenden
if st.button("🔄 Refresh"):
    # Business-Logik ausführen
    process_data()
    # UI-Refresh anfordern
    request_refresh()

# In MQTT-Callbacks
def on_message_received():
    # Nachricht verarbeiten
    process_message()
    # UI-Refresh anfordern (thread-sicher)
    request_refresh()
```

## Konsequenzen

### Positiv:
- **Thread-Sicherheit:** Keine Race Conditions
- **Stabilität:** Vermeidung von Endlosschleifen
- **Performance:** Effiziente UI-Updates
- **Konsistenz:** Einheitliches Update-Verhalten
- **Debugging:** Vorhersagbare UI-Updates

### Negativ:
- **Abhängigkeit:** Komponenten abhängig von UI-Refresh-Utils
- **Komplexität:** Zusätzliche Abstraktionsebene

## Implementierung

- [x] `request_refresh()` Funktion in `ui_refresh.py`
- [x] Thread-sichere UI-Updates
- [x] Vermeidung von `st.rerun()` in Komponenten
- [x] MQTT-Callback-sichere Updates
- [x] Einheitliche Verwendung in allen Komponenten

---

*Entscheidung getroffen von: OMF-Entwicklungsteam*
