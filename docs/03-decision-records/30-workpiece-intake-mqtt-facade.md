# Decision Record: Workpiece-Intake MQTT-Facade

**Datum:** 2026-08-20  
**Status:** Accepted  
**Kontext:** Object Detection und künftige OSF-Views brauchen ein Signal „neues Werkstück / NFC an DPS“, ohne APS-Interna (`module/…`, `RGB_NFC`, FTS-`load[]`) an Partner freizugeben. OSF-UI im Browser ist kein zuverlässiger Publisher (nur aktiv bei geöffneter Session). Session Manager läuft nur lokal am Laptop.

---

## Entscheidung

1. **Topic:** `osf/workpiece/intake` (ORBIS-Event, kein OD-spezifischer Namespace).
2. **Publisher:** schlanke **Bridge** als Docker-Container auf dem Shopfloor-RPi (`osf-workpiece-intake-bridge`), immer an, amselben MQTT-Netz wie `mqtt-broker-prod`.
3. **Payload (minimal):** `productRaw`, `nfc`, `timestamp`. **Kein** `orderId` — zum Intake-Zeitpunkt liefert APS noch `"0"`; die echte Order-UUID entsteht später (FTS/CCU, oft Storage-Order) und gehört nicht in die Intake-Facade. Track&Trace/Persistenz korrelieren über NFC.
4. **Nicht** über TXT-DPS-Firmware; **nicht** über osf-ui; **nicht** über Session Manager; Persistenz/SQL ist späterer Auswerte-Pfad, nicht Live-Quelle.
5. **Zielarchitektur:** langfristig kann **DSP** (statt CCU/Node-RED) dasselbe Topic befüllen; Bridge ist Übergang und kann wachsen. `osf/` ≠ nur osf-ui (Namespace für ORBIS-MQTT, vgl. DR-18).
6. **Farbe:** Publish erst, wenn APS eine bekannte Farbe liefert (kein `UNKNOWN`); erstes `RGB_NFC` oft nur NFC, ~1 s später mit `metadata.type`.

## Nachtrag 25.08.2026

- Live: `orderId` am DPS-Intake praktisch nie gesetzt → aus Vertrag entfernt (kein zweites Topic nur für Storage-`orderId`).
- Live: Farbe-Wait-Logik in der Bridge bestätigt.

## Nachtrag 26.08.2026 — Intake als kanonischer Einstieg (UI + Replay)

**Entscheidung:** Replay und fehlende historische Zeilen dürfen **keine Dual-Pfad-Architektur** in OSF-UI erzwingen. Die Bridge bleibt der Publisher; **OSF-UI subscribed** `osf/workpiece/intake` als Einstieg für Track&Trace (History-Bootstrap). APS-`INPUT_RGB`/`RGB_NFC`-Sonderlogik in T&T wird **abgebaut**, nicht parallel gepflegt.

**Reihenfolge:**
1. Dieses DR (Nachtrag) + Sprint-Task scharf formulieren.
2. OSF-UI: Subscribe + History aus Intake; APS-Intake-Bootstrap schrumpfen.
3. Session Manager / Doku: neue Aufnahmen erwarten Intake (Bridge live; Topic nicht in Exclusion-Presets).
4. Session-Logs: **alle relevanten mit Storage-Orders** um Intake-Zeilen anreichern (ASCII, nahe dem bisherigen `RGB_NFC`/`INPUT_RGB`). Übrige Sessions: Mehrwert prüfen → behalten oder löschen (`INVENTORY.md`).

**Konsequenz Doku:** Formulierungen „Intake nur live / nicht in Replay“ (ältere How-tos, DR-28-Kontext) gelten als **Übergangszustand**, nicht als Zielbild.

## Alternativen

- **APS-Topics an Partner:** leakt Steuerungsdetails — verworfen.
- **osf-ui als Publisher:** nur bei offenem Browser — verworfen für Shopfloor-Wahrheit.
- **Session Manager:** nur Laptop — verworfen.
- **Edge-Persistence publish:** Stack read-only / Grafana-Fokus — nicht als Live-Facade; Persistenz bleibt speichern, nicht ersetzen.
- **Topic `osf/od/…`:** koppelt Event an eine App — verworfen; generisches Intake-Event.

## Konsequenzen

- **Positiv:** stabile Kante für OD und OSF; APS gekapselt; passt zur DSP-Story.
- **Negativ:** zusätzlicher Container am RPi; Bridge muss APS-`RGB_NFC` kennen (intern).
- **Risiken:** Doppel-Publishes bei NodeRed+TXT — Dedup in der Bridge (TTL).

## Implementierung

- [x] Service `osf-workpiece-intake-bridge/`
- [x] How-to Deploy RPi
- [x] Image auf RPi laden + Compose-Service aktiv (25.08.2026)
- [x] OSF-UI subscribed Intake als T&T-Einstieg; APS-Bootstrap abgebaut; RPi **1.3.0** (26.08.2026)
- [x] Session-Logs mit Storage-Orders um Intake patchen; Rest inventarisieren (26.08.2026: Script + 38 Zeilen; Startup/2-AGV/synthetic behalten)

---
*Entscheidung getroffen von: Oliver Berger*
