# Arduino MQTT-Kopplung via Ethernet Shield 2

**Hardware:** Arduino Uno + Ethernet Shield 2 (W5500)  
**Ziel:** Arduino mit LAN in das APS-Netz einbinden und MQTT-Publishing für Vibrationssensor implementieren  

**IP- und Topic-Schema:** [DR-18 OSF-Erweiterungen](../03-decision-records/18-osf-extensions-ip-and-mqtt-topics.md)

---

## 0. Vorbereitung in der Arduino IDE (ohne Ethernet Shield)

Diese Schritte können **bereits jetzt** erledigt werden, bevor das Ethernet Shield 2 geliefert wird:

| Schritt | Aktion |
|---------|--------|
| 1 | **Libraries installieren:** Sketch → Bibliothek einbinden → Bibliotheken verwalten → `Ethernet2` und `PubSubClient` suchen und installieren |
| 2 | **Arduino per USB verbinden** – Board mit Computer verbinden (USB-Typ-B-Kabel) |
| 3 | **Sketch öffnen:** Datei → Sketchbook → Vibrationssensor_SW420 |
| 4 | **Board & Port wählen:** Werkzeuge → Board → Arduino Uno; Werkzeuge → Port → (erscheint nach USB-Verbindung) |
| 5 | **`USE_MQTT` prüfen:** Oben im Sketch steht `#define USE_MQTT 0` – damit läuft nur Serial (lokal), MQTT-Code ist vorbereitet aber inaktiv |
| 6 | **Kompilierung testen:** Häkchen (Verify) – Sketch muss ohne Fehler kompilieren |

**Ergebnis:** Der Sketch enthält bereits das Ethernet/MQTT-Gerüst. Sobald das Shield montiert und verbunden ist, `USE_MQTT` auf `1` setzen und neu hochladen.

---

## 1. Übersicht: Netzwerk-Architektur APS

| Bereich         | IP-Bereich      | Verwendung                    | DHCP/Statisch |
|-----------------|-----------------|-------------------------------|---------------|
| Gateway         | 192.168.0.1     | TP-Link Router                | -             |
| OPC-UA Module   | 192.168.0.40-90 | MILL, DRILL, OVEN, AIQS, HBW, DPS | Statisch  |
| Raspberry Pi    | 192.168.0.100   | MQTT Broker (Mosquitto), Node-RED, Dashboard | Statisch |
| DHCP/WLAN       | 192.168.0.101-199 | TXT-Controller, Cloud Gateway | DHCP         |

**MQTT-Broker:** `192.168.0.100:1883` (Mosquitto auf Raspberry Pi)

---

## 2. IP-Adress-Variante: Empfehlung

### Option A: DHCP (192.168.0.101–199)

| Pro                          | Contra                                      |
|-----------------------------|---------------------------------------------|
| Keine manuelle Konfiguration | IP kann sich bei Neuverbindung ändern       |
| Einfacher Einstieg          | Debugging schwieriger (IP unbekannt)        |
| Wie TXT-Controller          | Kein stabiler Eintrag in Doku/Config        |

**Einsatz:** Nur für erste Tests; IP wird dann im `connection`-Topic mitgeliefert.

### Option B: Statische IP (empfohlen)

| Pro                            | Contra                     |
|--------------------------------|----------------------------|
| Stabile, dokumentierbare IP    | Einmalige Konfiguration    |
| Keine Änderungen bei Neustart  | Router/DHCP muss bereinigt bleiben |
| Konsistent mit OPC-UA-Modulen  | -                          |

**Empfohlener IP-Bereich für Arduino/Sensoren:** `192.168.0.91–99`  
(aktuell frei, zwischen DPS 90 und Raspberry Pi 100)

**Vorschlag für Arduino Vibrationssensor:**
- **IP:** `192.168.0.95`
- **Gateway:** `192.168.0.1`
- **Subnetz:** `255.255.255.0`
- **DNS:** nicht erforderlich (kein HTTPS/HTTP)

> Optional: Bei mehreren Arduinos: 95, 96, 97… in diesem Bereich vergeben.

---

## 3. Hardware-Anforderungen

| Komponente       | Status     | Anmerkung                                                  |
|------------------|-----------|------------------------------------------------------------|
| Arduino Uno      | bestellt  | Rev3                                                       |
| Ethernet Shield 2| bestellt  | W5500-Chip, kompatibel mit offizieller Ethernet2-Library   |
| SW-420 Sensor    | vorhanden | Digital, Pin 2                                            |
| 4-Ch Relais      | vorhanden | Ampel-Steuerung                                            |

**Verdrahtung:** siehe [arduino-vibrationssensor.md](arduino-vibrationssensor.md).

---

## 4. Software-Anforderungen (Arduino IDE)

### 4.1 Libraries

| Library        | Version    | Zweck                         |
|----------------|------------|-------------------------------|
| Ethernet2      | 1.0.x      | Ethernet Shield 2 (W5500)     |
| PubSubClient   | 2.8.x      | MQTT Client                   |

**Installation:**  
Arduino IDE → Werkzeuge → Library Manager → „Ethernet2“ und „PubSubClient“ installieren.

### 4.2 Konfiguration (Sketch)

```cpp
// Netzwerk - Statisch (Empfehlung)
IPAddress ip(192, 168, 0, 95);
IPAddress gateway(192, 168, 0, 1);
IPAddress subnet(255, 255, 255, 0);

// ODER - DHCP (nur für Tests)
// Keine ip/gateway/subnet - Ethernet.begin(mac) ruft DHCP auf

// MQTT
const char* MQTT_BROKER = "192.168.0.100";
const int MQTT_PORT = 1883;
const char* MQTT_CLIENT_ID = "arduino_sw420_1";
```

### 4.3 Wichtige PubSubClient-Grenzen

- **Max Message Size:** ca. 256 Bytes (konfigurierbar via `setBufferSize()`)
- **Max Packet Size:** Standard 128 Bytes – für JSON-State evtl. erhöhen

---

## 5. MQTT-Topic-Schema (bereits definiert)

| Topic                                           | Zweck                 |
|-------------------------------------------------|------------------------|
| `osf/arduino/vibration/sw420-1/state`          | Status (Ampel, Impulse)|
| `osf/arduino/vibration/sw420-1/connection`     | LWT, Online-Status + IP|
| `osf/arduino/vibration/sw420-1/value`          | (optional) Rohwert    |

Details: [DR-18 OSF-Erweiterungen](../03-decision-records/18-osf-extensions-ip-and-mqtt-topics.md)

---

## 6. Implementierungs-Checkliste

- [ ] Ethernet Shield 2 auf Arduino Uno stecken
- [ ] Ethernet-Kabel zum Router/Switch stecken
- [ ] `Ethernet2` und `PubSubClient` installieren
- [ ] Sketch um MQTT erweitern (siehe Abschnitt 7)
- [ ] IP wählen: 192.168.0.95 (statisch) oder DHCP
- [ ] MQTT-Broker erreichen: `ping 192.168.0.100` vom Arduino (oder Netzwerk-Test)
- [ ] Topics testen: `mosquitto_sub -h 192.168.0.100 -t 'osf/arduino/#' -v`

---

## 7. Sketch-Struktur (Stichworte für Implementation)

```
setup():
  - Ethernet.begin(mac) bzw. Ethernet.begin(mac, ip, gateway, subnet)
  - Warten auf DHCP-Lease (falls DHCP) oder sofort weiter
  - mqttClient.setServer(MQTT_BROKER, MQTT_PORT)
  - mqttClient.setCallback(onMessage)  // falls Subscribe nötig
  - Publish connection: {"online":true,"ip":"192.168.0.95"}
  - LWT (Last Will) registrieren: connection mit {"online":false}

loop():
  - mqttClient.loop()
  - Sensor lesen (digitalRead)
  - Bei Vibration: state publishen, Relais schalten
```

---

## 8. Zusammenfassung

| Aspekt           | Empfehlung                                      |
|------------------|--------------------------------------------------|
| **IP-Vergabe**   | Statisch: `192.168.0.95`                         |
| **MQTT-Broker**  | `192.168.0.100:1883`                             |
| **Client-ID**    | `arduino_sw420_1`                                |
| ** Topics**      | `osf/arduino/vibration/sw420-1/*`               |
| **Libraries**    | Ethernet2, PubSubClient                          |

**IP-Bereich ORBIS Extensions:**  
`192.168.0.91–99` – dokumentiert in [DR-18](../03-decision-records/18-osf-extensions-ip-and-mqtt-topics.md), credentials.md, hardware-architecture.md, module-serial-mapping.md.
