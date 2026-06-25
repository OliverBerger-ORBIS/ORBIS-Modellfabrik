# 🎯 Object Detection Capture (MVP)

## Zweck

Der Tab **Object Detection** bereitet Datenerfassung so vor, dass pro Aufnahme nur noch ein klarer Workflow noetig ist:

1. Session-Name setzen
2. Preflight pruefen
3. OD-Session starten
4. Video manuell starten (MVP)
5. OD-Session stoppen
6. Video stoppen und im Session-Ordner ablegen

Ziel ist ein sauberer **2-Feed-Export** fuer AI-HUB:
- Feed 1: Video (`video.mp4`)
- Feed 2: Minimales MQTT-Meta (`meta_min.jsonl` mit `order_id`, `nfc_tag`, optional `phase`)

Andere Shopfloor-Events koennen optional separat gespeichert werden (`events_full.log`) und sind nicht Teil des Minimal-Feeds.

---

## Ablage

Basis:

`data/osf-data/sessions/object-detection/`

Pro Session:

`data/osf-data/sessions/object-detection/<session_name>/`

Dateien je Session:
- `manifest.json` (Setup, Zeiten, Zaehler, letzter erkannter `order_id`/`nfc_tag`)
- `meta_min.jsonl` (Minimal-Feed fuer AI-HUB)
- `events_full.log` (optional, nur QA/Korrelation)
- `video.mp4` (manuell abgelegt; Dateiname im Tab konfigurierbar)

---

## Workflow im Tab

## 1) Session vorbereiten

- `Session-Name` eingeben (z. B. `object-detection_white-1`)
- Ablage-Basisverzeichnis pruefen/anpassen
- Video-Dateiname festlegen (Default `video.mp4`)
- Topic-Filter setzen (`#` oder eingeschraenkte Filter)
- Optional: `events_full.log` aktivieren
- Optional: Preset-Ausschluss fuer `events_full.log` setzen:
  - `none`
  - `exclude_cam`
  - `exclude_aps_sensors`
  - `exclude_arduino`
  - `exclude_all_sensors`

## 2) Preflight

Der Tab prueft:
- Session-Name gueltig
- paho-mqtt verfuegbar
- Ablagepfad beschreibbar
- Session-Ordner noch nicht vorhanden (oder bereits aktiv in derselben laufenden Session)
- Broker erreichbar
- Single-Instance-Check fuer lokale Broker (wenn host lokal)
- Topic-Filter gesetzt

Nur bei gruener Pruefung startet die Session.

## 3) OD-Session starten

- Klick auf `OD-Session starten`
- MQTT-Subscribe auf `#`
- Automatische Anlage/Initialisierung von `manifest.json` und `meta_min.jsonl`
- `meta_min.jsonl` und optionale `events_full.log` werden bereits waehrend der Aufnahme fortlaufend geschrieben
- Minimale Event-Extraktion aus Payloads:
  - Order-Felder: `orderId`, `order_id`, `productionOrderId`, `transportOrderId`
  - NFC-Felder: `nfcTag`, `nfc_tag`, `nfcId`, `nfc_id`, `tagId`

## 4) Video starten (MVP manuell)

Video wird im MVP nicht aus dem Session Manager fernbedient. Start in OBS (oder aehnlich) erfolgt manuell.

## 5) OD-Session stoppen

- Klick auf `OD-Session stoppen`
- MQTT sauber trennen
- `manifest.json` mit Endzeit und Event-Zaehlern finalisieren

## 6) Video stoppen und ablegen

- Videoaufnahme stoppen
- Datei in denselben Session-Ordner legen (Dateiname wie im Manifest konfiguriert)

---

## Hinweise

- Der MVP ist auf robuste Datenerfassung ausgelegt, nicht auf Vollautomation.
- Bei Windows-Stop/Restart sorgt Cleanup beim Beenden dafuer, dass MQTT-Loop und Dateihandler sauber geschlossen werden.
- V2-Erweiterung (optional): OBS-WebSocket Start/Stop direkt aus dem Tab.
