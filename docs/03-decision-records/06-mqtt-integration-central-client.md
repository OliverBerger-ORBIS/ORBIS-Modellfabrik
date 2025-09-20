# Decision Record: MQTT-Integration über zentralen Client

**Datum:** 2024-12-19  
**Status:** Accepted  
**Kontext:** Das OMF-Dashboard benötigt eine einheitliche MQTT-Integration mit zentralem Logging und konsistenter Payload-Behandlung.

---

## Entscheidung

Verwendung des **Singleton MQTT-Clients** für alle MQTT-Operationen mit zentralem Logging in `omf_mqtt_client.py`.

```python
# Alle MQTT-Publish-Aufrufe gehen über Singleton-Client
result = mqtt_client.publish(topic, payload, qos=1, retain=False)

# Gateway-Logging in omf_mqtt_client.py
def publish(self, topic: str, payload, qos: int = 1, retain: bool = False) -> bool:
    data = payload if isinstance(payload, (bytes, bytearray)) else json.dumps(payload)
    
    # Log Topic und Payload beim Senden
    if isinstance(payload, (bytes, bytearray)):
        payload_str = payload.decode('utf-8', errors='replace')
    else:
        payload_str = data  # data ist bereits json.dumps(payload)
    self.logger.info(f"📤 MQTT Publish: {topic} → {payload_str}")
    
    res = self.client.publish(topic, data, qos=qos, retain=retain)
```

## Konsequenzen

### Positiv:
- **Einheitlichkeit:** Alle MQTT-Operationen zentral verwaltet
- **Logging:** Automatisches Logging aller MQTT-Nachrichten
- **Konsistenz:** Einheitliche Payload-Behandlung
- **Performance:** Effiziente JSON-Serialisierung
- **Debugging:** Vollständige Nachverfolgung von MQTT-Traffic

### Negativ:
- **Abhängigkeit:** Alle Komponenten abhängig von zentralem Client
- **Komplexität:** Zusätzliche Abstraktionsebene

## Implementierung

- [x] Singleton MQTT-Client über `ensure_dashboard_client()`
- [x] Zentrale Logging-Funktion in `omf_mqtt_client.py`
- [x] Dictionary-Payloads statt String-Payloads
- [x] Effiziente JSON-Serialisierung (keine doppelte)
- [x] Einheitliche Fehlerbehandlung

---

*Entscheidung getroffen von: OMF-Entwicklungsteam*
