# Arduino IDE Setup

**Zielgruppe:** Entwickler*innen, die Arduino-Projekte der APS-Modellfabrik (z. B. Vibrationssensor, Ethernet Shield) programmieren  
**Letzte Aktualisierung:** 02.2026

---

## 🎯 Übersicht

Dieses How-To beschreibt die Einrichtung der **Arduino IDE** als Entwicklungsumgebung für Arduino-basierte Hardware-Projekte im ORBIS-Modellfabrik-Kontext. Es ist eine **Voraussetzung** für die Umsetzung von Projekten wie der [Arduino R4 Multi-Sensor](../../05-hardware/arduino-r4-multisensor.md).

**Separation:** Setup (dieses Dokument) vs. Projekt-Inhalte (Hardware-Dokumentation, Code):  
Das Setup enthält nur die Installation und Konfiguration der IDE. Was konkret gebaut und programmiert wird, steht in den jeweiligen Projekt-Dokumenten.

---

## 📋 Voraussetzungen

- **Arduino Uno** (oder kompatibles Board)
- **USB-Kabel** (Typ A/B oder je nach Board)
- **Internetverbindung** (für Board Manager, Libraries)

---

## 1. Arduino IDE installieren

### Download

- **Offizielle Seite:** [arduino.cc/en/software](https://www.arduino.cc/en/software)
- **Empfohlene Version:** Arduino IDE 2.x (aktuellste stabile Version)

### Installation (Plattform-spezifisch)

| Plattform | Vorgehen |
|----------|----------|
| **Windows** | Installer herunterladen und ausführen. USB-Treiber werden mitinstalliert (bei Problemen siehe Abschnitt Troubleshooting). |
| **macOS** | `.dmg` herunterladen, Arduino.app in den Programme-Ordner ziehen. Kein zusätzlicher Treiber für Uno nötig. |
| **Linux** | Paketmanager nutzen (`sudo apt install arduino` / `sudo dnf install arduino`) oder von arduino.cc installieren. User zur Gruppe `dialout` hinzufügen: `sudo usermod -a -G dialout $USER` (danach neu anmelden). |

---

## 2. Board & Port einrichten

### Board auswählen

1. **Arduino IDE öffnen**
2. **Werkzeuge → Board → Arduino-Board**
3. **Arduino Uno** auswählen (oder Arduino Mega, falls verwendet)

### Serial Port (USB)

1. **Arduino per USB verbinden**
2. **Werkzeuge → Port**
3. Port wählen:
   - **Windows:** z. B. `COM3`, `COM4`
   - **macOS:** z. B. `/dev/cu.usbmodem14101`
   - **Linux:** z. B. `/dev/ttyACM0`

> **Hinweis:** Wenn kein Port erscheint, siehe [Troubleshooting](#troubleshooting).

---

## 3. Sketchbook-Speicherort (integrations/Arduino)

Damit die Arduino-Projekte des ORBIS-Modellfabrik-Repos direkt in der IDE verfügbar sind, den **Sketchbook-Speicherort** auf den Ordner `integrations/Arduino` setzen:

1. **Arduino IDE** → **Einstellungen** (File → Preferences / Arduino IDE → Settings)
2. **Sketchbook-Speicherort** auf den absoluten Pfad setzen:
   - z. B. `/Users/oliver/Projects/ORBIS-Modellfabrik/integrations/Arduino` (macOS/Linux)
   - z. B. `C:\Users\...\ORBIS-Modellfabrik\integrations\Arduino` (Windows)
3. **OK** klicken und Arduino IDE **neu starten**

Danach erscheinen die Sketches (z. B. `Vibrationssensor_SW420`) im Menü **Datei → Sketchbook** und können direkt geöffnet werden.

---

## 4. Bibliotheken (Libraries)

Für das Projekt **Vibrationsüberwachung** (SW-420, Relais) reichen die Standard-Bibliotheken. Für **Ethernet Shield 2** oder **MPU-6050** (Ausblick) werden zusätzliche Libraries benötigt.

### Library Manager

1. **Sketch → Bibliothek einbinden → Bibliotheken verwalten**
2. Nach Name suchen (z. B. `Ethernet2`, `MPU6050`)
3. **Installieren** klicken

### Typische Libraries (bei Bedarf)

| Library      | Verwendung                         |
|--------------|------------------------------------|
| Ethernet2    | Arduino Ethernet Shield 2 (W5500)  |
| PubSubClient | MQTT für LAN-Anbindung             |
| Wire         | I2C (z. B. MPU-6050) – meist schon enthalten |

---

## 5. Systemtest (Hardware-Software-Check)

Bevor die eigentliche Projektverkabelung beginnt, muss sichergestellt werden, dass der Computer den Mikrocontroller korrekt anspricht. Dies geschieht über den **Blink-Test**.

### 5.1 Verbindung herstellen

Verbinde den Arduino Uno über das USB-Typ-B-Kabel mit dem Computer.

Die grüne „ON“-LED auf dem Board muss leuchten.

### 5.2 Port- und Board-Konfiguration

- Wähle im oberen Dropdown-Menü das Board **Arduino Uno** aus.
- Stelle sicher, dass der zugehörige Port (z. B. `COM3` unter Windows oder `/dev/cu.usbmodem...` unter macOS) mit einem Häkchen markiert ist.

### 5.3 Laden des Beispiel-Sketches

Navigiere zu: **Datei → Beispiele → 01.Basics → Blink**.

Es öffnet sich ein neues Fenster mit dem fertigen Test-Code.

### 5.4 Kompilieren und Hochladen

1. Klicke auf das **Häkchen-Symbol** (Verify), um den Code zu kompilieren. In der Statuszeile muss „Done compiling“ erscheinen.
2. Klicke auf den **Pfeil nach rechts** (Upload). Der Code wird auf den Arduino geschrieben. Währenddessen blinken die TX/RX-LEDs auf dem Board.

### 5.5 Erfolgskontrolle

Der Test ist erfolgreich abgeschlossen, wenn:

- die Statuszeile der IDE „Done uploading“ anzeigt;
- die auf dem Arduino fest verbaute **orangerote LED** (markiert mit „L“) im Rhythmus von einer Sekunde blinkt.

Damit ist nachgewiesen, dass die Entwicklungsumgebung einsatzbereit ist.

---

## 6. Nächste Schritte

- **Arduino R4 Multi-Sensor:** [Verdrahtung & Konfiguration](../../05-hardware/arduino-r4-multisensor.md)
- **Sketch öffnen:** Datei → Sketchbook → OSF_MultiSensor_R4WiFi
- **integrations/Arduino:** [README](../../../integrations/Arduino/README.md)

---

## 7. Troubleshooting

### Kein Port sichtbar

| Ursache                 | Lösung |
|-------------------------|--------|
| Kabel lose/defekt       | USB-Kabel prüfen, anderes Kabel testen |
| Treiber fehlt (Windows) | CH340/CP2102-Treiber installieren (bei Clones); bei Original Arduino: Treiber neu installieren |
| Keine Berechtigung (Linux) | `sudo usermod -a -G dialout $USER`, danach neu anmelden |

### Upload schlägt fehl

- Port erneut prüfen
- Anderes USB-Kabel nutzen (manche Kabel sind nur Ladekabel, ohne Datenleitung)
- Arduino kurz vom USB trennen und wieder verbinden

### Ethernet Shield 2

- Shield fest auf Uno aufstecken
- Für Ethernet: Bibliothek `Ethernet2` verwenden (nicht die alte `Ethernet`)

---

## 🔗 Verwandte Dokumentation

- [Arduino R4 Multi-Sensor](../../05-hardware/arduino-r4-multisensor.md) – Hardware, Verdrahtung, MQTT
- [Project Setup](project-setup.md) – Allgemeine Projekt-Entwicklungsumgebung (Python, MQTT, …)
- [TXT-Controller Deployment mit ROBO Pro](../txt-controller-deployment.md) – Vergleichbare Trennung: Setup (RoboPro installiert) vs. Deployment-Workflow
