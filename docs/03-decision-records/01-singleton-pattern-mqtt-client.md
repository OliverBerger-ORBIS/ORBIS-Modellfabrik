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

---

*Entscheidung getroffen von: OMF-Entwicklungsteam*
