# 📚 Table of Contents – `/docs/07-analysis/`

Diese Datei enthält eine Übersicht aller funktionalen Analysen der bestehenden APS-Komponenten. Sie dient dem schnellen Einstieg und der strukturierten Navigation – sowohl für Entwickler als auch für den CURSOR-Agenten.

---

## Übersicht

- [MQTT Client Analyse](mqtt-client-analysis.md)
  - Übersicht der Publisher & Subscriber
  - Verwendete Topics
  - Mapping zu Modulen
- [FT-Module Verhalten](ft-module-behavior.md)
  - Beschreibung der .ft-Dateien
  - IO-Port Nutzung, Steuerlogik
  - Modul-zu-MQTT-Verhalten
- [CCU UI Tabs](ccu-ui-tabs.md)
  - Analyse der WebUI-Tabs der APS
  - Funktionen je Tab
  - Technische Zuordnung (MQTT/API)
- [OPC UA Struktur](opcua-structure.md)
  - Node-Struktur der TXT-Controller
  - Beobachtete Services und Tags
- [Docker Setup APS](aps-docker-setup.md)
  - Container-Struktur auf dem RPi
  - Dienste: CCU, Mosquitto, Node-RED

---

## Hinweise

- Neue Analysen bitte als eigene `.md` Datei anlegen
- Diese TOC-Datei regelmäßig pflegen
- Verlinkungen in anderen Doku-Teilen immer auf diesen TOC verweisen
