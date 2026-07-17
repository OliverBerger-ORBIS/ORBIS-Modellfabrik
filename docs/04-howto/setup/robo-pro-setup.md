# ROBO Pro Coding Setup

**Zielgruppe:** Entwickler*innen, die TXT-Controller der APS-Modellfabrik programmieren und Code deployen  
**Letzte Aktualisierung:** 17.07.2026

---

## 🎯 Übersicht

Dieses How-To beschreibt die **Installation von ROBO Pro Coding**, der offiziellen Programmierungsumgebung für fischertechnik TXT-Controller. Es ist eine **Voraussetzung** für das [TXT-Controller Deployment](../txt-controller-deployment.md) und alle Projekte in `integrations/TXT-*/`.

**Separation:** Setup (dieses Dokument) vs. Deployment-Inhalte (öffnen, ändern, deployen):  
Das Setup enthält nur die Installation der App. Der Workflow zum Öffnen von `.ft`-Archiven, Code-Änderungen und Deployment steht im [TXT-Controller Deployment How-To](../txt-controller-deployment.md).

---

## 📋 Voraussetzungen

- **TXT 4.0 Controller** (oder kompatibler fischertechnik Controller)
- **Internetverbindung** (für App-Download)
- **Apple-ID / Microsoft-Konto** (für App-Store-Installation, je nach Plattform)

---

## 1. Download & Installation

### Offizielle Quelle

**ROBO Pro Coding** ist die offizielle fischertechnik App für Block-basierte und Python-Programmierung. Alle Downloads über die offiziellen Kanäle:

| Plattform | Download | Hinweis |
|-----------|----------|---------|
| **Windows** | [Microsoft Store](https://apps.microsoft.com/store/detail/robo-pro-coding/9MXPK52R734C?hl=de-de&gl=de) | Suche: „ROBO Pro Coding“ |
| **macOS** | [Apple App Store](https://apps.apple.com/us/app/robo-pro-coding/id1569643514) | Auch für iOS (iPad) |
| **Linux** | [Direkt-Download ZIP](https://update.fischertechnik-cloud.com/repository/ft-roboprocoding-public/ft-roboprocoding-linux-STABLE.zip) | Entpacken und ausführen |
| **Android** | [Google Play Store](https://play.google.com/store/apps/details?id=eu.beemo.roboprocoding) | Für Tablets; Deployment i. d. R. über PC/Mac |

**Übersicht aller fischertechnik-Apps:** [fischertechnik.de/apps-und-software](https://www.fischertechnik.de/de-de/apps-und-software)

---

### Plattform-spezifische Schritte

#### Windows

1. **Microsoft Store öffnen** (im Startmenü suchen)
2. Nach **„ROBO Pro Coding“** suchen
3. **„Installieren“** oder **„Herunterladen“** klicken
4. Nach der Installation über das Startmenü oder die Taskleiste starten

#### macOS

1. **App Store** öffnen
2. Nach **„ROBO Pro Coding“** (Hersteller: fischertechnik) suchen
3. **„Laden“** / **„Installieren“** klicken
4. App aus dem Programme-Ordner oder über Spotlight starten

#### Linux

1. ZIP von der offiziellen URL herunterladen
2. Archiv entpacken:
   ```bash
   unzip ft-roboprocoding-linux-STABLE.zip
   cd ft-roboprocoding-linux-*
   ```
3. Ausführbare Datei starten (je nach Paket: `.AppImage`, Skript oder ähnlich)
4. Optional: Verknüpfung/Desktop-Shortcut anlegen

> **Hinweis:** Unter Linux können sich Datei- und Startpfade je nach fischertechnik-Version unterscheiden. Bei Problemen siehe [Troubleshooting](#troubleshooting).

---

## 2. Erste Schritte nach der Installation

### App starten

1. **ROBO Pro Coding** öffnen
2. Die App zeigt die Startoberfläche (Projektliste oder Begrüßungsbildschirm)

### Erste Verifikation (ohne Controller)

1. **☰ → Projekt → Laden → Lokal** → eine `.ft` aus `integrations/TXT-*/archives/` öffnen  
   (z. B. `TXT-DPS/archives/FF_DPS_24V.ft` oder `TXT-AIQS/archives/FF_AI_24V_cam_clfn.ft`)
2. Rechts oben **Dateiliste** einblenden → unter `lib/` Module sichtbar?
3. Wenn Blockly/Python-Ansicht erscheint, ist die Installation korrekt
4. Deployment, Blockly-Fallen, Toolbar: [TXT-Controller Deployment](../txt-controller-deployment.md)

### Controller-Verbindung (optional zum Testen)

Die eigentliche Verbindung und das Deployment sind im [TXT-Controller Deployment How-To](../txt-controller-deployment.md) beschrieben. Kurzüberblick:

- **WLAN:** gleiches Netz wie TXT (Demo-/FT-LAN)
- **Verbinden / Deploy:** App-Toolbar (nicht macOS-Menüleiste) — Details im How-To
- **API-Key:** Vom Controller-Display ablesen
- **USB:** Alternative für erste Tests

---

## 3. Nächste Schritte

- **Deployment-Workflow:** [TXT-Controller Deployment mit ROBO Pro Coding](../txt-controller-deployment.md)
- **Projekt-Archive:** `integrations/TXT-{MODULE}/archives/`
- **Entscheidungsgrundlagen:** [Decision Record 17](../03-decision-records/17-txt-controller-deployment.md)

---

## 4. Troubleshooting

### App startet nicht (Windows)

- **Windows Defender / Antivirus:** Prüfen, ob ROBO Pro Coding blockiert wird
- **Store-Reparatur:** `Einstellungen → Apps → ROBO Pro Coding → Reparatur` (falls angeboten)
- **Neu installieren:** App deinstallieren und erneut aus dem Store installieren

### App startet nicht (macOS)

- **Sicherheitseinstellungen:** `Systemeinstellungen → Sicherheit` – App als vertrauenswürdig zulassen (falls Blockade angezeigt wird)
- **Gatekeeper:** Bei direkter Installation außerhalb des App Store: Rechtsklick → Öffnen

### Projekt öffnen schlägt fehl

- **Dateipfad:** Sonderzeichen, Umlaute und Leerzeichen im Pfad können Probleme verursachen
- **Archiv-Integrität:** `.ft`-Dateien nicht manuell (z. B. mit ZIP-Tools) bearbeiten – nur über ROBO Pro speichern

### Controller wird nicht gefunden

- Siehe [TXT-Controller Deployment – Troubleshooting](../txt-controller-deployment.md#-troubleshooting)
- Siehe [TXT-Controller Deployment – Troubleshooting](../txt-controller-deployment.md#-troubleshooting) für Controller-Verbindungsprobleme

---

## 5. Hinweis zur Plattform-Verfügbarkeit

ROBO Pro Coding wird von fischertechnik für **Windows, macOS, Linux, Android und iOS** angeboten. In älteren Projekt-Dokumenten steht teils „nur Mac“ – das ist veraltet; die App ist für alle genannten Plattformen verfügbar.

---

## 🔗 Verwandte Dokumentation

- [TXT-Controller Deployment mit ROBO Pro Coding](../txt-controller-deployment.md) – Workflow: Öffnen, Ändern, Deployen
- [Arduino IDE Setup](arduino-ide-setup.md) – Vergleichbares Setup für Arduino-Projekte
- [Project Setup](project-setup.md) – Allgemeine Entwicklungsumgebung (Python, MQTT, …)
