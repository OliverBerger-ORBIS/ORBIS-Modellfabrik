# OSF Arduino R4 Multi-Sensor – Verdrahtung & Konfiguration

**Hardware:** Arduino Uno R4 WiFi, MPU-6050, SW-420, DHT11, Flammensensor KY-026, MQ-2, 4-Kanal-Relais, 12V-Signalampel (Grün/Gelb/Rot/Sirene)

**Sketch:** `OSF_MultiSensor_R4WiFi` (Version im Sketch-Header: `SKETCH_VERSION`)  
**Diagramm:** [arduino-r4-multisensor-verdrahtung.mermaid](arduino-r4-multisensor-verdrahtung.mermaid)

**Voraussetzung:** [Arduino IDE Setup](../04-howto/setup/arduino-ide-setup.md) – zuerst Blink-Test durchführen.

---

## 0. Architektur-Prinzip: Wahrheit liegt beim Arduino

**Single Source of Truth:** Schwellen und Klassifikation (normal/warning/alarm) werden ausschließlich im Arduino-Sketch definiert. Die osf-ui interpretiert keine Rohwerte – sie zeigt nur an, was der Sensor publiziert.

| Aspekt | Arduino | osf-ui |
|--------|---------|--------|
| Schwellen (Flame, Gas, DHT) | ✓ definiert | — |
| Klassifikation (gasLevel 0/1/2) | ✓ berechnet | nur Darstellung |
| Raw-Wert | ✓ gemessen, gesendet | nur Anzeige |

**Folge:** Änderungen an Schwellen nur im Sketch; Sensor-Tab **Rahmenfarben** für DHT nutzen dieselben Grenzwerte wie der Sketch (siehe `sensor-tab.component.ts`, Konstanten neben Arduino). **DHT-Luftfeuchte (Stand Sketch v1.1.1):** Warn (Gelb) ab **60 %**, Alarm (Rot) ab **85 %** (Temp unverändert: 30 °C / 35 °C). Deployment: Serial Monitor „Sketch v1.1.x“ prüfen.

---

## 1. WLAN-Konfiguration (Sketch)

Im Sketch oben: `#define WIFI_MODE WIFI_MODE_DAHEIM` oder `WIFI_MODE_ORBIS`.

| Modus | WLAN | Arduino-IP | Gateway | MQTT-Broker |
|-------|------|------------|---------|-------------|
| **DAHEIM** | Heimnetz (SSID/Passwort anpassen) | 192.168.178.95 | 192.168.178.1 | 192.168.178.65 (Mac) |
| **ORBIS** | ORBIS-4C57 (Messe LogiMAT 2026; vgl. [credentials](../credentials.md)) | 192.168.0.95 | 192.168.0.1 | 192.168.0.100 |

Nur diese eine Zeile ändern, neu kompilieren, flashen. Bei DAHEIM: Arduino-IP in der Fritz!Box reservieren (z.B. .95).

---

## 2. 5V & Signal (Arduino → Breadboard → Sensoren → Relais)

### 2.1 Stromverteilung Breadboard

| Von | Nach | Kabel |
|-----|------|-------|
| Arduino **5V** | Breadboard **(+)** Bus | ROT |
| Arduino **GND** | Breadboard **(−)** Bus | SCHWARZ |

### 2.2 MPU-6050 (I2C)

| Sensor | Breadboard/Arduino |
|--------|--------------------|
| VCC | (+) Bus |
| GND | (−) Bus |
| SDA | Arduino **A4** |
| SCL | Arduino **A5** |

### 2.3 SW-420

| Sensor | Breadboard/Arduino |
|--------|--------------------|
| VCC | (+) Bus |
| GND | (−) Bus |
| DO | Arduino **D11** |

### 2.4 DHT11 (3-Pin: links −, Mitte +, rechts S)

| Sensor | Breadboard/Arduino |
|--------|--------------------|
| Mitte (VCC) | (+) Bus |
| Links (−) GND | (−) Bus |
| Rechts (S) Data | Arduino **D12** |

### 2.5 Flammensensor KY-026

| Sensor | Breadboard/Arduino |
|--------|--------------------|
| VCC | (+) Bus |
| GND | (−) Bus |
| AOut (analog) | Arduino **A1** |

### 2.6 MQ-2 Gas-Sensor (Rauch/CO)

| Sensor | Breadboard/Arduino |
|--------|--------------------|
| VCC | (+) Bus |
| GND | (−) Bus |
| AOut (analog) | Arduino **A0** |

### 2.7 4-Kanal Relais (5V-Steuerung)

| Relais | Arduino | Ampel |
|--------|---------|-------|
| IN1 | **D7** | Grün |
| IN2 | **D8** | Gelb |
| IN3 | **D9** | Rot |
| IN4 | **D10** | Sirene |

Relais aktiv-niedrig: LOW = ein, HIGH = aus. Ruhe = Grün ein (D7 LOW).

---

## 3. 12V & Ampel (Netzteil → Relais → Ampel)

### 3.0 Alternative: 12 V aus 24 V-APS (Molex / Step-Down)

Liegt die Sensorstation an einer **24 V-Kaskade** und soll **ohne separates 12 V-Steckernetzteil** auskommen: **ein** DC/DC **24 V→12 V** (z. B. Funduino **F23105924** / XL4005), gemeinsame **12 V-Schiene** für Relais/Ampel und **Arduino VIN** — vollständige BOM, Mermaid-Schema, **DAHEIM vs. ORBIS** (USB + Tisch‑12 V vs. APS) → [sensor-station-24v-bom-wiring.md](sensor-station-24v-bom-wiring.md). **Relais, Ampel und Common Ground** in den folgenden Abschnitten bleiben unverändert; nur die **Quelle** für 12 V+ / 12 V− weicht ab.

### 3.1 COM-Kette (alle COMs an 12V+)

| Verbindung | Beschreibung |
|------------|--------------|
| 12V(+)** → **COM1** | Rotes Kabel vom Netzteil (+) |
| **COM1 ↔ COM2** | Brücke (Draht/Schraubklemme) |
| **COM2 ↔ COM3** | Brücke |
| **COM3 ↔ COM4** | Brücke |

**Wichtig:** Alle vier COMs müssen durchgängig mit 12V+ verbunden sein.

### 3.2 Relais-Ausgänge → Ampel

| Relais NO | Ampel-Anschluss |
|-----------|-----------------|
| **NO1** | Grün |
| **NO2** | Gelb |
| **NO3** | Rot |
| **NO4** | Sirene |

### 3.3 Ampel Common

| Ampel Common | 12V Netzteil (−) |
|--------------|------------------|
| Common (alle Lampen minus) | 12V(−) |

### 3.4 Common Ground (obligatorisch)

| Breadboard (−) | 12V-Netzteil (−) |
|---------------|------------------|
| Schwarzes M/M-Kabel | Verbindung zu 12V(−) |

Ohne Common Ground kann die Relais-Logik fehlschlagen.

---

## 4. MQTT & Publish-Verhalten

**Publish-Logik:** Bei Zustandsänderung sofort; bei Idle alle **5 s** als Heartbeat (MQTT_HEARTBEAT_INTERVAL). Schnellere UI-Aktualisierung als bei 15 s, Overhead vernachlässigbar.

**Sketch-Versionierung:** SemVer im Header (`#define SKETCH_VERSION "1.1.x"`). Bei jedem Deployment Version anpassen. Serial Monitor zeigt „Sketch v1.1.x“ beim Start. Gängige Praxis: Version im Code, ggf. Git-Tag für Releases.

**Deployment-Checkliste:**
1. `SKETCH_VERSION` im Sketch-Header anpassen (z.B. 1.1.0 → 1.2.0)
2. Arduino IDE: Sketch öffnen, Board „Arduino Uno R4 WiFi“, Port wählen
3. Upload, Serial Monitor (9600): „Sketch v1.1.x“ prüfen
4. MQTT: `mosquitto_sub -h <broker> -t "osf/arduino/#" -v` – alle Sensoren melden?

---

## 5. MQTT-Topics

| Topic | Inhalt |
|------|--------|
| `osf/arduino/vibration/mpu6050-1/state` | `{"vibrationLevel":"green\|yellow\|red","vibrationDetected":bool,"magnitude":n,"timestamp":"…"}` (ISO UTC mit ms, z. B. `…T12:05:01.234Z`) |
| `osf/arduino/vibration/mpu6050-1/connection` | LWT, Online-Status, IP |
| `osf/arduino/vibration/sw420-1/state` | `{"vibrationDetected":bool,"impulseCount":n,"timestamp":"…"}` |
| `osf/arduino/vibration/sw420-1/connection` | LWT |
| `osf/arduino/temperature/dht11-1/state` | `{"temperature":n,"humidity":n,"temperatureUnit":"C","humidityUnit":"%","timestamp":"…"}` |
| `osf/arduino/temperature/dht11-1/connection` | LWT |
| `osf/arduino/flame/flame-1/state` | `{"flameDetected":bool,"rawValue":n}` |
| `osf/arduino/flame/flame-1/connection` | LWT |
| `osf/arduino/gas/mq2-1/state` | `{"gasDetected":bool,"gasLevel":0\|1\|2,"rawValue":n,"timestamp":"…"}` – gasLevel: 0=normal, 1=warning, 2=alarm |
| `osf/arduino/gas/mq2-1/connection` | LWT |
| `osf/arduino/alarm/enabled` | **Subscribe:** `true`/`false` – Sirene nur bei Alarm, wenn Toggle aktiv |

**Sirene aktivieren (Test):**
```bash
mosquitto_pub -h 192.168.178.65 -t "osf/arduino/alarm/enabled" -m "true"
```

**Alle Sensoren abhören:**
```bash
mosquitto_sub -h 192.168.178.65 -t "osf/arduino/#" -v
```

**Warnung/Alarm — kontinuierliche Telemetrie (Sketch v1.1.3+):** Während die **Gesamtampel** gelb oder rot ist, wird der **MPU-State** zusätzlich alle **2 s** gesendet (aktualisierte `magnitude`/`vibrationLevel`). **DHT-, SW-420-, Flammen- und Gas-Topics** ebenfalls alle **2 s**, solange der jeweilige Sensor im **eigenen** Warn- oder Alarmband ist (`dhtLevel` / Vibration / `flameDetected` / `gasDetected`). Im reinen **Grün**-Betrieb bleibt der **5 s**-Heartbeat pro Topic. Hintergrund: Nur „Publish bei Level-Wechsel“ ließ Rohwerte in der OSF-UI im gleichen Warnband stehen (z. B. steigende Luftfeuchte bei konstantem Gelb).

**`timestamp` in State-Payloads (Sketch v1.1.4+):** ISO-8601 **UTC**. **v1.1.6:** mit **Millisekunden** (`YYYY-MM-DDThh:mm:ss.sssZ`), aus **Sync-Zeit (Sekunden)** plus **Offset aus `millis()`** seit letztem Sync. Ohne UTC bleibt der Wert `""`. **v1.1.5+:** Kein **NTPClient**; Zeit über **`WiFi.getTime()`** + **rohes UDP-NTP** zu Gateway/Öffentlich; **`gUtcEpochBase` + `millis()`** zwischen Syncs; alle 2 s **`WiFi.getTime()`** zur Driftkorrektur. **UDP-Port 123** ausgehend zur NTP-Ziel-IP beachten.

---

## 6. Checkliste Verdrahtung

### 5V-Seite
- [ ] 5V vom Arduino an Breadboard (+)
- [ ] GND vom Arduino an Breadboard (−)
- [ ] MPU-6050: VCC/GND an BB, SDA→A4, SCL→A5
- [ ] SW-420: VCC/GND an BB, DO→**D11**
- [ ] DHT11: Mitte→5V, links−→GND, rechts S→**D12**
- [ ] Flamme: VCC/GND an BB, AOut→**A1**
- [ ] MQ-2 Gas: VCC/GND an BB, AOut→**A0**
- [ ] Relais: VCC/GND an BB, IN1→D7, IN2→D8, IN3→D9, IN4→D10

### 12V-Seite
- [ ] 12V(+) an COM1
- [ ] COM1–COM2–COM3–COM4 durchgängig verbunden (Brücken prüfen!)
- [ ] NO1→Grün, NO2→Gelb, NO3→Rot, NO4→Sirene
- [ ] Ampel Common → 12V(−)

### Common Ground
- [ ] Breadboard (−) mit 12V(−) verbunden

---

## 7. Fehlersuche

**Ampel leuchtet nicht:**
1. **COM-Kette:** Mit Multimeter prüfen – zwischen COM1 und COM4 darf kein Widerstand sein.
2. **12V an COM:** Zwischen COM1 und 12V(−) sollten ~12V anliegen.
3. **NO-Kontakte:** Bei aktivem Relais (D7 LOW für Grün) sollte zwischen NO1 und Common Durchgang sein.
4. **Common Ground:** Breadboard(−)–12V(−) verbinden.

**MQTT verbindet nicht:**
- Broker-IP erreichbar? `ping 192.168.178.65`
- Mosquitto läuft? `lsof -i :1883`
- Arduino im gleichen Netz? Fritz!Box-Reservierung für .95 prüfen.

**Sirene schaltet nicht:** Toggle `osf/arduino/alarm/enabled` auf `true` setzen (osf-ui oder mosquitto_pub). Sirene nur bei Alarm (Rot-Stufe) aktiv.

---

## 8. Referenzen

- **IP- und Topic-Schema:** [DR-18 OSF-Erweiterungen](../03-decision-records/18-osf-extensions-ip-and-mqtt-topics.md)
- **Credentials:** [credentials.md](../credentials.md) (ORBIS-Netz)
- **Inventar:** [inventory-electronics.md](inventory-electronics.md)
