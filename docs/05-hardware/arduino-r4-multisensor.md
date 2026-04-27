# OSF Arduino R4 Multi-Sensor – Verdrahtung & Konfiguration

**Hardware:** Arduino Uno R4 WiFi, MPU-6050, SW-420, DHT11, Flammensensor KY-026, MQ-2, 4-Kanal-Relais, 12V-Signalampel (Grün/Gelb/Rot/Sirene)

**Sketch:** `OSF_MultiSensor_R4WiFi` (Version im Sketch-Header: `SKETCH_VERSION`)  
**Diagramm:** [arduino-r4-multisensor-verdrahtung.mermaid](arduino-r4-multisensor-verdrahtung.mermaid)

**Voraussetzung:** [Arduino IDE Setup](../04-howto/setup/arduino-ide-setup.md) – zuerst Blink-Test durchführen.

---

## 0. Architektur-Prinzip: Wahrheit liegt beim Arduino

**Single Source of Truth (Firmware):** Schwellen und Klassifikation sind im **Sketch** und im **Factsheet** (`osf/arduino/station/factsheet`, retained) dokumentiert. Die osf-ui interpretiert keine Rohwerte in Telemetrie – sie zeigt an, was der Sensor publiziert.

**Laufzeit-Anpassung (optional, selten):** Über **`osf/arduino/station/config`** können Schwellen in **RAM** gesetzt werden (OSF **Configuration**-Tab). Nach **Reset/Neustart** gelten wieder die Sketch-Defaults; dauerhafte Werte gehören in eine **neue Sketch-Version** und Flash.

| Aspekt | Arduino | osf-ui |
|--------|---------|--------|
| Schwellen (Flame, Gas, DHT) | ✓ definiert + Factsheet | Configuration: Anzeige + optional MQTT-Config |
| Klassifikation (gasLevel 0/1/2) | ✓ berechnet | nur Darstellung |
| Raw-Wert | ✓ gemessen, gesendet | nur Anzeige |

**Folge:** Environmental Data (Sensor-Tab): DHT-Warn-/Alarm-Rahmen folgen **`osf/arduino/station/factsheet`** (retained), sobald empfangen; sonst Sketch-Defaults wie in `draftFromThresholdsOnly` (z. B. 30/35 °C, 60/85 % rel.). **DHT-Luftfeuchte (Stand Sketch v1.1.1):** Warn (Gelb) ab **60 %**, Alarm (Rot) ab **85 %**. Deployment: Serial Monitor „Sketch v1.1.x“ prüfen.

---

## 1. WLAN-Konfiguration (Sketch)

**Standard (Repo):** **ORBIS** — kein Zusatzfile nötig (`WIFI_MODE_ORBIS`, MQTT `192.168.0.100`).

**Wechsel ohne Commit (lokal):** `wifi_mode_local.h.example` nach `wifi_mode_local.h` kopieren (liegt im Sketch-Ordner, wird per `.gitignore` nicht committed) und darin `WIFI_MODE` auf `WIFI_MODE_DAHEIM` oder `WIFI_MODE_ORBIS` setzen. Fehlt `wifi_mode_local.h`, gilt weiterhin **ORBIS**.

| Modus | WLAN | Arduino-IP | Gateway | MQTT-Broker |
|-------|------|------------|---------|-------------|
| **DAHEIM** | Heimnetz (SSID/Passwort anpassen) | 192.168.178.95 | 192.168.178.1 | 192.168.178.65 (Mac) |
| **ORBIS** | ORBIS-4C57 (vgl. [credentials](../credentials.md)) | 192.168.0.95 | 192.168.0.1 | 192.168.0.100 |

Neu kompilieren, flashen. Bei DAHEIM: Arduino-IP in der Fritz!Box reservieren (z.B. .95).

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

**Publish-Logik:** Kombiniert: **sofort** bei Zustands-/Level-Wechseln (Alarm-Reaktion) **und zusätzlich periodische Telemetrie** für Korrelation mit Shopfloor-Events (Zeitreihe der Rohwerte). *(Stand: Sketch v1.1.12)*.

**Sketch-Versionierung:** SemVer im Header (`#define SKETCH_VERSION "1.1.x"`). Bei jedem Deployment Version anpassen. Serial Monitor zeigt „Sketch v1.1.x“ beim Start. Gängige Praxis: Version im Code, ggf. Git-Tag für Releases.

**Deployment-Checkliste:**
1. `SKETCH_VERSION` im Sketch-Header anpassen (z.B. 1.1.0 → 1.2.0)
2. Arduino IDE: Sketch öffnen, Board „Arduino Uno R4 WiFi“, Port wählen
3. Upload, Serial Monitor (9600): „Sketch v1.1.x“ prüfen
4. MQTT: `mosquitto_sub -h <broker> -t "osf/arduino/#" -v` – alle Sensoren melden?

**Upgrade Notes v1.1.9:** State-Topics publish-on-change (keine periodischen 2s Re-Publishes mehr bei Warnung/Alarm).
**Upgrade Notes v1.1.10:** SW-420 triggert nur **Gelb** (nicht Rot); zusätzlich moderate Entprellung + Print-Drossel im Serial Monitor. MPU-Schwellen: Gelb=18000, Rot=36000.
**Upgrade Notes v1.1.11:** Fix: `lastPublishedGasLevel` korrekt initialisiert (kein doppeltes Gas-State Publish direkt nach Boot). Debug-Print nutzt eigenes Tracking und funktioniert damit auch im Serial-only Modus (`USE_MQTT=0`).
**Upgrade Notes v1.1.12:** Periodische Telemetrie-Publishes wieder aktiv (MPU ~1s, DHT ~5s, Flame/Gas ~2s) zusätzlich zu sofortigen Zustandswechsel-Events – wichtig für Event-Korrelation.

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
| `osf/arduino/station/factsheet` | **Publish (retained):** Ein JSON mit `sketchVersion`, `stationId`, `configTopic`, `thresholds` (aktuelle Schwellen) und **`sensors`[]** (id, label, stateTopic, capabilities). Wird nach MQTT-Verbindung publiziert. |
| `osf/arduino/station/config` | **Subscribe:** JSON `{"thresholds":{...}}` mit Feldern wie `dhtTempWarn`, `dhtTempDanger`, `gasWarn`, `gasDanger`, `flameRaw`, `mpuMagnitudeYellow`, `mpuMagnitudeRed` – nur **RAM**, kein Flash. |

**Sirene aktivieren (Test):**
```bash
mosquitto_pub -h 192.168.178.65 -t "osf/arduino/alarm/enabled" -m "true"
```

**Alle Sensoren abhören:**
```bash
mosquitto_sub -h 192.168.178.65 -t "osf/arduino/#" -v
```

**Warnung/Alarm — Event + Telemetrie (Sketch v1.1.12+):** State-Topics werden **sofort** bei Zustandswechsel publiziert (z. B. Ampel `green→red→yellow→green`) und zusätzlich **periodisch** als Telemetrie (Rohwerte), damit sich Sensorwerte mit Shopfloor-Events korrelieren lassen.

**Vibration (MPU vs. SW-420):**
- **MPU-6050** bestimmt Gelb/Rot über `mpuMagnitudeYellow` / `mpuMagnitudeRed`.
- **SW-420** ist ein binärer Vibrationsschalter und wird als **Gelb-Warnung** verwendet (kein Rot-Alarm); Signal wird moderat entprellt (ca. 50 ms Confirm + kurzer Hold).

**`timestamp` in State-Payloads (Sketch v1.1.4+):** ISO-8601 **UTC**. **v1.1.6:** mit **Millisekunden** (`YYYY-MM-DDThh:mm:ss.sssZ`), aus **Sync-Zeit (Sekunden)** plus **Offset aus `millis()`** seit letztem Sync. Ohne UTC bleibt der Wert `""`. **v1.1.7:** In **`WIFI_MODE_ORBIS`** wird **NTP** zuerst gegen den **Shopfloor-RPi** (`192.168.0.100`, **chrony**) versucht, danach Gateway und öffentliche Pools — siehe [rpi-chrony-ntp-server.md](../04-howto/rpi-chrony-ntp-server.md). **v1.1.5+:** Kein **NTPClient**; Zeit über **`WiFi.getTime()`** + **rohes UDP-NTP** zu Gateway/Öffentlich; **`gUtcEpochBase` + `millis()`** zwischen Syncs; alle 2 s **`WiFi.getTime()`** zur Driftkorrektur. **UDP-Port 123** ausgehend zur NTP-Ziel-IP beachten.

**ORBIS / Firmennetz — leere `timestamp`:** Steht im Serial Monitor z. B. `WARN: keine UTC – timestamp leer (NTP: UDP 123 ausgehend?)`, sind **WLAN und MQTT** oft trotzdem in Ordnung; es scheitert nur die **UTC-Synchronisation**. Häufig: **`WiFi.getTime()`** liefert vom Access Point keine Zeit; **UDP 123** ausgehend ist zu **öffentlichen** NTP-Servern oder zum **Gateway** gesperrt; oder der **Router** antwortet nicht auf NTP.

**Lokaler NTP auf dem RPi (gleiches 192.168.x-Netz):** Auf dem **Shopfloor-RPi** (Broker im ORBIS-LAN typisch **`192.168.0.100`**, Arduino z. B. **`192.168.0.95`**) kann **chrony** auf dem **Host** als NTP-Server für das LAN laufen (**`allow`** in `/etc/chrony/conf.d/`). Einrichtung: [rpi-chrony-ntp-server.md](../04-howto/rpi-chrony-ntp-server.md). **Sketch v1.1.7+** trägt **`192.168.0.100`** in **`WIFI_MODE_ORBIS`** als **ersten** NTP-Server ein (`servers[]` / Fallback) — nach RPi-Setup neu flashen. Vorab im LAN prüfen: `sntp -d 192.168.0.100`.

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

**`timestamp` in MQTT leer, Serial `WARN: keine UTC`:** Siehe **§5** (ORBIS/Firmennetz, NTP). Kurz: **UDP 123** / interner **NTP** (z. B. **RPi** im gleichen Subnetz) oder Sketch-Serverliste anpassen.

**Sirene schaltet nicht:** Toggle `osf/arduino/alarm/enabled` auf `true` setzen (osf-ui oder mosquitto_pub). Sirene nur bei Alarm (Rot-Stufe) aktiv.

---

## 8. Referenzen

- **IP- und Topic-Schema:** [DR-18 OSF-Erweiterungen](../03-decision-records/18-osf-extensions-ip-and-mqtt-topics.md)
- **Credentials:** [credentials.md](../credentials.md) (ORBIS-Netz)
- **Inventar:** [inventory-electronics.md](inventory-electronics.md)
