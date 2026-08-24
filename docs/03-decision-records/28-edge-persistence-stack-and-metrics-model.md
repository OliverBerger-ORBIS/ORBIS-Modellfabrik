# Decision Record: Edge Persistence Stack und generisches Sensor-Metrikmodell

**Datum:** 2026-05-08  
**Status:** Accepted  
**Kontext:** Sprint 21, Aufgabe "Backend & Grafana" verlangt persistente Datenhaltung fuer Prozess-, Shopfloor- und Umweltdaten inkl. Dashboarding. Historisch wurde ein Influx-basierter Metrics-Service vorbereitet. Fuer den Zielbetrieb wurde nun entschieden, Persistenz und Visualisierung auf einen DSP-Edge-Knoten zu verlagern und ein relationales Zeitreihenmodell zu nutzen.

> **Vorgehensweise:** Wann/Wie ein Decision Record erstellt wird -> [README - Vorgehensweise](README.md#vorgehensweise-wann-wird-ein-decision-record-erstellt)

---

## Entscheidung

1. **Zielplattform fuer Persistenz und Visualisierung ist der DSP-Edge-Knoten.**  
   Der APS-RPi bleibt primaer operative Steuerungskomponente (CCU/Node-RED/MQTT) und soll nicht dauerhaft mit DB- und Dashboard-Last belastet werden.

2. **Deploy bleibt in Phase 1 variabel.**  
   Neben dem Zielzustand "Edge" werden explizit `local-dev` (Mac/Notebook) und `rpi-pilot` als gueltige Betriebsmodi unterstuetzt, um Infrastrukturabhaengigkeit in der Einfuehrung zu vermeiden.

3. **Primare Datenbank ist PostgreSQL + TimescaleDB.**  
   Begruendung: kombinierte Auswertung von Zeitreihen und relationalen Entitaeten (Order, Steps, Workpieces, Event-Korrelation).

4. **MQTT-Ingest ist strikt read-only.**  
   Der Persistence-Service subscribet Topics und publiziert keine Steuerkommandos in Richtung APS.

5. **Sensorpersistenz folgt einem generischen Metrikmodell.**  
   `sensor_snapshot` wird nicht mit festen Spalten pro Sensor aufgebaut, sondern als metric-orientiertes Schema (z. B. `sensor_type`, `metric_name`, `value_numeric`, `value_text`, `unit`), damit TXT- und Arduino-Sensorik gleichbehandelt und erweiterbar bleiben.

6. **Sensordaten werden selektiv persistiert.**  
   Persistenz nur bei `EVENT`, `THRESHOLD` oder konfiguriertem `INTERVAL`, nicht als ungefilterter Vollstream.  
   **Aktive Orders (`ccu/order/active` nicht leer):** `INTERVAL = 5 s`. **Idle:** `INTERVAL = 60 s`. Warn/Alarm (Arduino `vibrationLevel` yellow/red, `flameDetected`, `gasLevel >= 1`) immer als `THRESHOLD`.

7. **Topic-Konventionen bleiben kompatibel zu bestehenden OSF-Regeln.**  
   Bestehendes DR-18-Schema fuer OSF-Sensorik (`osf/arduino/<sensorTyp>/<deviceId>/<action>`) bleibt erhalten. Kein erzwungener Topic-Rename als Voraussetzung fuer den Persistence-Stack.

8. **Kamera-Topic bleibt von der Standardpersistenz ausgeschlossen.**  
   `/j1/txt/1/i/cam` wird nicht in der Kernpersistenz gespeichert.

---

## Alternativen

- **RPi als dauerhafte DB/Grafana-Host-Plattform:** verworfen, um operative APS-Stabilitaet, I/O und Ressourcen fuer CCU/Node-RED/MQTT zu priorisieren.
- **InfluxDB als primaeres Ziel beibehalten:** verworfen als Zielarchitektur fuer diesen Ausbaupfad; bleibt als bestehende Alternative/Legacy-Variante dokumentiert.
- **Feste Sensor-Spalten (temperature/humidity/...) pro Snapshot:** verworfen, da schlechte Erweiterbarkeit fuer heterogene Arduino-/OSF-Sensorik.
- **Topic-Namensmigration fuer Arduino erzwingen:** verworfen, da kein direkter Mehrwert fuer die Persistenzfunktion und unnoetige Umstellung bestehender Publisher/Tools.

---

## Nachtrag (21.07.2026) – Track & Trace Persistenz

**Entscheidung:** Die OSF-UI-Live-Demo (`WorkpieceHistoryService`) bleibt **session-/RAM-scoped** (Clear bei Header-Refresh / Reload). Längere NFC-/Ereignis-Historien (nach B-soft logischen IDs) gehören in den **Edge-Persistence-/Grafana-Pfad** (`shopfloor_event` / `workpiece`, Dashboard `workpiece-trace`) — **kein** paralleles Browser-localStorage für Genealogie. UI-Anbindung an die Edge-DB ist eine spätere Aufgabe, sobald Ingest stabil ist.

---

## Konsequenzen

- **Positiv:**
  - Klare Entkopplung: APS operativ, Edge analytisch.
  - Bessere Traceability durch relationale + zeitbasierte Auswertung in einem Modell.
  - Erweiterbare Sensorintegration ohne Schema-Neuentwurf bei neuen Metriken.
  - Gleicher Stack auf `local-dev`, `rpi-pilot` und `edge-prod` erleichtert Tests.

- **Negativ:**
  - Zusaetzlicher Betriebs-Stack (Postgres/Timescale + Grafana + Persistence-Service).
  - Migrations-/Abgrenzungsbedarf gegenueber bestehender Influx-Dokumentation.

- **Risiken:**
  - Doppelte Wahrheiten in Doku, falls Legacy- und Zielarchitektur nicht sauber markiert werden.
  - Inkonsistente Event-Keys ohne fruehe Idempotenzregeln.

---

## Nachtrag (20.08.2026) – NFC als Universal-ID, Replay vs Live

**Live:** eindeutige NFC-Tags (B-soft) sind der Korrelationsschlüssel (`workpiece_id`). Intake-Topic `osf/workpiece/intake` ist eine **RPi-Bridge-Facade** und in Session-Logs **nicht** enthalten.

**Replay (Home-Office):** NFC kommt aus denselben APS-Feldern wie Track&Trace (`RGB_NFC.result`, FTS `loadId`, CCU `workpieceId`). Eine lokale Intake-Bridge ist nicht nötig. Unterschiedliche Sessions mit unterschiedlichen NFC-IDs dürfen in der lokalen DB akkumulieren. Truncate nur **manuell** (`scripts/reset-replay-db.sh`), nicht bei jedem Replay.

---

## Nachtrag (24.08.2026) – Sensorik an Ist-Events

Arduino-/TXT-Payloads tragen keine NFC-ID. Die Kopplung Sensor ↔ Werkstück ist **query-time** (as-of: letzter `sensor_snapshot` vor dem Ist-Event im konfigurierten Fenster), analog zur RAM-ENV-Snapshot-Logik in Track & Trace. `sensor_snapshot.related_event_id` / `workpiece_id` werden beim Ingest **nicht** befüllt. Auswertung: `db/queries/sensor_around_ist_event.sql` bzw. `scripts/sensor-around-ist.sh`.

**Sensor-INTERVAL (24.08.2026, Korrektur):** Default war irrtümlich 3600 s. Fachlich: **5 s bei aktiven Orders**, **60 s idle**, Alarme/Warnungen immer. Volume bleibt unkritisch gegenüber Timescale-Retention (365 Tage Snapshots).

**Soll-Topics (24.08.2026):** Zusätzlich subscribed: `ccu/order/request`, `ccu/order/response`, `module/v1/ff/+/order` (inkl. NodeRed), `fts/v1/ff/+/order`. Ablage in `mqtt_raw_message` und `shopfloor_event` (`REQUESTED` / `RESPONDED` bzw. Kommando ohne FINISHED). Grafana-Ist filtert weiter nur `FINISHED` — kein Vermischen von Soll und Ist.

---

## Implementierung (Soll)

- [ ] Stack `osf-edge-persistence` mit Docker Compose (Postgres/Timescale, Grafana, Persistence-Service) angelegt
- [ ] Environment-Matrix dokumentiert: `local-dev`, `rpi-pilot`, `edge-prod`
- [ ] Topic-Ingest read-only umgesetzt (CCU/Module/FTS/TXT + OSF-Sensorik)
- [ ] Generisches `sensor_snapshot`-Schema umgesetzt
- [ ] Sensorpersistenz-Regeln (`EVENT`/`THRESHOLD`/`INTERVAL`) zentral konfigurierbar
- [ ] `/j1/txt/1/i/cam` explizit ausgeschlossen
- [ ] Grafana Provisioning (Datasource + Starter-Dashboards) versioniert
- [ ] Legacy-Hinweis fuer Influx-Metrics-Doku gesetzt

---
*Entscheidung getroffen von: Team OSF / ORBIS SmartFactory*
