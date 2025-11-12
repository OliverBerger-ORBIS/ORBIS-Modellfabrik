# Module Docking Command Preconditions

**Datum:** 2025-11-12  
**Kontext:** PR-10 Modules Tab (Angular)

## Ausgangslage
- Die OMF2-Implementierung (Streamlit) bietet im `factory_steering_subtab` einen Button "Docke an" für das FTS.
- Die OMF3-Angular-Anwendung übernimmt die Verantwortung für Steuerbefehle über den Pfad Business → Gateway → MQTT-Client.
- Startup-Sessions zeigen, dass das FTS nach dem Einschalten `lastModuleSerialNumber: "UNKNOWN"` sendet und erst nach erfolgreichem Andocken einen konkreten Modul-Seriennamen liefert.

## Entscheidung
Das Docking-Kommando wird nur angeboten, wenn **alle** folgenden Bedingungen erfüllt sind:
1. Das FTS ist in `moduleOverview.transports` vorhanden.
2. `transport.lastModuleSerialNumber` fehlt oder ist exakt `"UNKNOWN"`.
3. Die Pairing-Payload meldet `availability: "BLOCKED"` (Startup-Zustand vor dem Andocken).

Damit spiegeln wir die OMF2-Bedienlogik wider: Der Button erscheint initial, verschwindet jedoch, sobald das FTS erfolgreich an einem Modul angedockt hat.

## Konsequenzen
- UI: Der Module-Tab zeigt den Button "Dock" nur unter obigen Bedingungen an.
- Business-Layer: Muss die Pairing-Snapshots zusammen mit Factsheets auswerten, um `lastModuleSerialNumber` und `availability` zu tracken.
- Gateway: Liefert weiterhin die Rohdaten aus den Topics `ccu/pairing/state` und `fts/v1/...`.
- Fixture-Setup: Die Startup-Session (`Start_20251110_175151.log`) dient als Referenzfall und reproduziert den Zustand `lastModuleSerialNumber: "UNKNOWN"`.

## Offene Punkte
- Zusätzliche Fixture-Dateien aus `data/omf-data/test_topics/preloads/*factsheet.json` können später integriert werden, sind für das Docking-Kommando jedoch nicht zwingend.
