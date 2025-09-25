# Decision Record: Singleton-Pattern für MQTT-Client

**Datum:** 2024-12-19  
**Status:** Accepted  
**Kontext:** Das OMF-Dashboard benötigt einen zentralen, einheitlichen MQTT-Client für alle Komponenten, um Ressourcenverschwendung zu vermeiden und Konsistenz zu gewährleisten.

---

## Entscheidung

Verwendung des **Singleton-Pattern** für den MQTT-Client über `ensure_dashboard_client()` in `omf_mqtt_factory.py`.

```python
def ensure_dashboard_client(env: str, store: MutableMapping) -> OmfMqttClient:
    """Singleton-Client für die Session"""
    cli = store.get("mqtt_client")
    if cli is None:
        cli = OmfMqttClient(cfg)
        cli.connect()
        store["mqtt_client"] = cli
    return cli
```

## Konsequenzen

### Positiv:
- **Ressourceneffizienz:** Nur ein MQTT-Client pro Session
- **Konsistenz:** Alle Komponenten verwenden denselben Client
- **Zentrale Verwaltung:** Ein Ort für Verbindungslogik
- **Session-Persistenz:** Client bleibt über Streamlit-Reruns erhalten

### Negativ:
- **Abhängigkeit:** Alle Komponenten abhängig von Session State
- **Komplexität:** Zusätzliche Abstraktionsebene

## Implementierung

- [x] `ensure_dashboard_client()` in `omf_mqtt_factory.py`
- [x] Session State Management in `omf_dashboard.py`
- [x] Alle Komponenten verwenden `st.session_state.get("mqtt_client")`
- [x] Keine direkten `OmfMqttClient` Instanzen in Komponenten
- [x] **Strenge Environment-Prüfung** zur Vermeidung von Connection-Loops
- [x] **Saubere Verbindungsbehandlung** mit `disconnect()` und `loop_stop()`

## Kritische Regeln (2025-09-25 Update)

**Connection-Loop Prevention:**
1. **Strenge Prüfung:** `stored_env != env` vor jedem Reconnect
2. **Saubere Trennung:** Alte Verbindungen mit `disconnect()` und `loop_stop()` trennen
3. **Fallback-Mechanismus:** Bei Reconnect-Fehlern neuen Client erstellen
4. **Zentrale Verwendung:** `ensure_dashboard_client()` nur in `omf_dashboard.py`

**Siehe auch:** [Decision Record 13: MQTT Connection-Loop Prevention](13-mqtt-connection-loop-prevention.md)

---

*Entscheidung getroffen von: OMF-Entwicklungsteam*
