# Decision Record: OSF-Erweiterungen – IP-Adressen und MQTT-Topics

**Datum:** 2026-02-18  
**Status:** ✅ **Accepted**  
**Kontext:** Integration von ORBIS-Erweiterungen (Arduino, Sensoren) neben Fischertechnik-APS. Entscheidung zu Netzwerk und MQTT-Namensschema.

---

## Entscheidung

### 1. IP-Adressbereich für ORBIS-Erweiterungen

**Bereich:** `192.168.0.91–99` (statisch)

- Zwischen OPC-UA-Modulen (40–90) und Raspberry Pi (100)
- Keine Überschneidung mit DHCP (101–199)
- **Arduino Vibrationssensor (sw420-1):** `192.168.0.95`
- Weitere Geräte: 96, 97, 98, 99 nach Bedarf

### 2. MQTT-Topic-Schema für OSF-Erweiterungen

**Pattern:** `osf/<plattform>/<sensorTyp>/<deviceId>/<action>`

| Segment    | Bedeutung     | Beispiel     |
|------------|---------------|--------------|
| `osf`      | ORBIS-Erweiterung (kein Fischertechnik v1/ff) | - |
| `plattform`| Hardware-Plattform | `arduino` |
| `sensorTyp`| Sensor-Kategorie | `vibration`, `temperature` |
| `deviceId` | Geräte-ID     | `sw420-1`, `mpu6050-1` |
| `action`   | Topic-Aktion  | `state`, `connection`, `value` |

**Arduino Vibrationssensor (SW-420):**

| Topic                                              | Zweck                         |
|----------------------------------------------------|-------------------------------|
| `osf/arduino/vibration/sw420-1/state`             | Status (ampel, impulseCount)   |
| `osf/arduino/vibration/sw420-1/connection`        | LWT, Online-Status, IP        |
| `osf/arduino/vibration/sw420-1/value`             | (optional) Rohwert            |

**state-Payload:**
```json
{
  "ampel": "GRUEN",
  "impulseCount": 0,
  "lastImpulseAt": "2026-02-23T12:05:00Z",
  "ts": "2026-02-23T12:05:01Z"
}
```
Werte für `ampel`: `GRUEN`, `ROT`, ggf. `GELB`.

---

## Alternativen

| Alternative | Beschreibung | Warum verworfen |
|-------------|--------------|-----------------|
| DHCP für Arduino | IP aus 101–199 | IP variabel, schlechter für Doku und Monitoring |
| `fabrik/` Namespace | Gemini-Vorschlag | „fabrik“ kein etablierter Namespace im Projekt |
| `dsp/vibration/` | An DSP-Demo angelehnt | dsp eher Demo/Edge; Sensoren grundlegender |

---

## Konsequenzen

- **Positiv:** Klare Trennung Fischertechnik (v1/ff) vs. ORBIS (osf); erweiterbar für weitere Sensoren (MPU-6050, Temperatur etc.)
- **Negativ:** Neuer Root-Namespace; Router/DHCP darf 91–99 nicht vergeben
- **Referenzen:** [mqtt-topic-conventions](../../06-integrations/00-REFERENCE/mqtt-topic-conventions.md), [arduino-mqtt-ethernet-setup](../../05-hardware/arduino-mqtt-ethernet-setup.md)
