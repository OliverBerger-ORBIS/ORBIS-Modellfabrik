# OSF Multi-Sensor (R4 WiFi) – Breadboard-Verdrahtung

**Sketch:** `OSF_MultiSensor_R4WiFi`  
**Diagramm:** [arduino-r4-multisensor-verdrahtung.mermaid](arduino-r4-multisensor-verdrahtung.mermaid)

---

## 1. 5V & Signal (Arduino → Breadboard → Sensoren → Relais)

### 1.1 Stromverteilung Breadboard

| Von | Nach | Kabel |
|-----|------|-------|
| Arduino **5V** | Breadboard **(+)** Bus | ROT |
| Arduino **GND** | Breadboard **(−)** Bus | SCHWARZ |

### 1.2 MPU-6050 (I2C)

| Sensor | Breadboard/Arduino |
|--------|--------------------|
| VCC | (+) Bus |
| GND | (−) Bus |
| SDA | Arduino **A4** |
| SCL | Arduino **A5** |

### 1.3 SW-420

| Sensor | Breadboard/Arduino |
|--------|--------------------|
| VCC | (+) Bus |
| GND | (−) Bus |
| DO | Arduino **D2** |

### 1.4 DHT11 (3-Pin: links −, Mitte +, rechts S)

| Sensor | Breadboard/Arduino |
|--------|--------------------|
| Mitte (VCC) | (+) Bus |
| Links (−) GND | (−) Bus |
| Rechts (S) Data | Arduino **D3** |

### 1.5 Flammensensor KY-026

| Sensor | Breadboard/Arduino |
|--------|--------------------|
| VCC | (+) Bus |
| GND | (−) Bus |
| AOut (analog) | Arduino **A0** |

### 1.6 MQ-2 Gas-Sensor (Rauch/CO)

| Sensor | Breadboard/Arduino |
|--------|--------------------|
| VCC | (+) Bus |
| GND | (−) Bus |
| AOut (analog) | Arduino **A1** |

### 1.7 4-Kanal Relais (5V-Steuerung)

| Relais | Arduino |
|--------|---------|
| VCC | (+) Bus |
| GND | (−) Bus |
| **IN1** | Arduino **D7** (Grün) |
| **IN2** | Arduino **D8** (Gelb) |
| **IN3** | Arduino **D9** (Rot) |
| **IN4** | Arduino **D10** (Sirene) |

---

## 2. 12V & Ampel (Netzteil → Relais → Ampel)

### 2.1 COM-Kette (alle COMs an 12V+)

| Verbindung | Beschreibung |
|------------|--------------|
| 12V(+)** → **COM1** | Rotes Kabel vom Netzteil (+) |
| **COM1 ↔ COM2** | Brücke (Draht/Schraubklemme) |
| **COM2 ↔ COM3** | Brücke |
| **COM3 ↔ COM4** | Brücke |

**Wichtig:** Alle vier COMs müssen durchgehend mit 12V+ verbunden sein. Eine unterbrochene Brücke = keine Lampe funktioniert.

### 2.2 Relais-Ausgänge → Ampel

| Relais NO | Ampel-Anschluss |
|-----------|-----------------|
| **NO1** | Grün |
| **NO2** | Gelb |
| **NO3** | Rot |
| **NO4** | Sirene |

### 2.3 Ampel Common

| Ampel Common | 12V Netzteil (−) |
|--------------|------------------|
| Common (alle Lampen minus) | 12V(−) |

---

## 3. Common Ground (obligatorisch)

| Breadboard (−) | 12V-Netzteil (−) |
|---------------|------------------|
| Schwarzes M/M-Kabel | Verbindung zu 12V(−) |

Ohne Common Ground kann die Relais-Logik fehlschlagen. **Breadboard GND und 12V(−) müssen verbunden sein.**

---

## 4. Checkliste Verdrahtung

### 5V-Seite
- [ ] 5V vom Arduino an Breadboard (+)
- [ ] GND vom Arduino an Breadboard (−)
- [ ] MPU-6050: VCC/GND an BB, SDA→A4, SCL→A5
- [ ] SW-420: VCC/GND an BB, DO→D2
- [ ] DHT11: Mitte→5V, links−→GND, rechts S→D3
- [ ] Flamme: VCC/GND an BB, AOut→A0
- [ ] MQ-2 Gas: VCC/GND an BB, AOut→A1
- [ ] Relais: VCC/GND an BB, IN1→D7, IN2→D8, IN3→D9, IN4→D10

### 12V-Seite
- [ ] 12V(+) an COM1
- [ ] COM1–COM2–COM3–COM4 durchgängig verbunden (Brücken prüfen!)
- [ ] NO1→Grün, NO2→Gelb, NO3→Rot, NO4→Sirene
- [ ] Ampel Common → 12V(−)

### Common Ground
- [ ] Breadboard (−) mit 12V(−) verbunden

---

## 5. Fehlersuche (Ampel leuchtet nicht)

1. **COM-Kette:** Mit Multimeter prüfen: Zwischen COM1 und COM4 darf kein Widerstand sein (durchgängig).
2. **12V an COM:** Zwischen COM1 und 12V(−) sollten ~12V anliegen (Netzteil eingeschaltet).
3. **NO-Kontakte:** Bei aktivem Relais (D7 LOW für Grün) sollte zwischen NO1 und Common Durchgang sein.
4. **Common Ground:** Ohne Verbindung Breadboard(−)–12V(−) können die Relais nicht sauber schalten.
