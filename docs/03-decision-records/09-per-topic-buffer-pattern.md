# Decision Record: Per-Topic-Buffer Pattern

**Datum:** 2024-12-19  
**Status:** Accepted  
**Kontext:** Das OMF-Dashboard benötigt eine effiziente MQTT-Nachrichtenverarbeitung mit Topic-spezifischen Puffern für bessere Performance und Organisation.

---

## Entscheidung

Verwendung des **Per-Topic-Buffer Pattern** mit `subscribe_many()` und `get_buffer()` für effiziente MQTT-Nachrichtenverarbeitung.

```python
# Subscribe-Many für mehrere Topics
mqtt_client.subscribe_many([
    "module/v1/ff/*/state",
    "module/v1/ff/*/connection", 
    "ccu/order/request",
    "ccu/set/*"
])

# Topic-spezifische Buffer abrufen
state_messages = mqtt_client.get_buffer("module/v1/ff/*/state")
order_messages = mqtt_client.get_buffer("ccu/order/request")

# Nachrichten verarbeiten
for message in state_messages:
    process_state_message(message)
```

## Konsequenzen

### Positiv:
- **Performance:** Effiziente Topic-Verwaltung
- **Organisation:** Nachrichten nach Topics gruppiert
- **Skalierbarkeit:** Viele Topics ohne Performance-Probleme
- **Flexibilität:** Topic-spezifische Verarbeitung
- **Memory-Effizienz:** Nur relevante Nachrichten im Buffer

### Negativ:
- **Komplexität:** Zusätzliche Abstraktionsebene
- **Lernkurve:** Entwickler müssen Pattern verstehen

## Implementierung

- [x] `subscribe_many()` für Topic-Subscription
- [x] `get_buffer()` für Topic-spezifische Nachrichten
- [x] Topic-Filter für Nachrichtenverarbeitung
- [x] Buffer-Management in `omf_mqtt_client.py`
- [x] Per-Topic-Verarbeitung in Komponenten

---

*Entscheidung getroffen von: OMF-Entwicklungsteam*
