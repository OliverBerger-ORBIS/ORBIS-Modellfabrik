# Decision Record: Session State Management

**Datum:** 2024-12-19  
**Status:** Accepted  
**Kontext:** Das OMF-Dashboard benötigt eine einheitliche Verwaltung von Manager-Instanzen und Zuständen über Streamlit-Reruns hinweg.

---

## Entscheidung

Verwendung von **Streamlit Session State** für Manager-Instanzen und persistente Zustände.

```python
# Manager in Session State speichern
if "aps_commands_manager" not in st.session_state:
    st.session_state["aps_commands_manager"] = APSCommandsManager()

manager = st.session_state["aps_commands_manager"]

# MQTT-Client aus Session State holen
client = st.session_state.get("mqtt_client")
if not client:
    st.error("❌ MQTT-Client nicht verfügbar")
    return
```

## Konsequenzen

### Positiv:
- **Persistenz:** Zustände bleiben über Reruns erhalten
- **Performance:** Manager-Instanzen werden nicht neu erstellt
- **Konsistenz:** Einheitliche Zustandsverwaltung
- **Einfachheit:** Streamlit-native Lösung

### Negativ:
- **Memory:** Zustände bleiben im Speicher
- **Komplexität:** Session State muss verwaltet werden

## Implementierung

- [x] Manager-Klassen in Session State speichern
- [x] MQTT-Client aus Session State abrufen
- [x] Fehlerbehandlung für fehlende Zustände
- [x] Einheitliche Namenskonvention für Keys
- [x] Lazy Initialization für Manager

---

*Entscheidung getroffen von: OMF-Entwicklungsteam*
