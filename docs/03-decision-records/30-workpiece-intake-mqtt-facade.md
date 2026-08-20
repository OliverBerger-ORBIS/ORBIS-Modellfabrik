# Decision Record: Workpiece-Intake MQTT-Facade

**Datum:** 2026-08-20  
**Status:** Accepted  
**Kontext:** Object Detection und künftige OSF-Views brauchen ein Signal „neues Werkstück / NFC an DPS“, ohne APS-Interna (`module/…`, `RGB_NFC`, FTS-`load[]`) an Partner freizugeben. OSF-UI im Browser ist kein zuverlässiger Publisher (nur aktiv bei geöffneter Session). Session Manager läuft nur lokal am Laptop.

---

## Entscheidung

1. **Topic:** `osf/workpiece/intake` (ORBIS-Event, kein OD-spezifischer Namespace).
2. **Publisher:** schlanke **Bridge** als Docker-Container auf dem Shopfloor-RPi (`osf-workpiece-intake-bridge`), immer an, amselben MQTT-Netz wie `mqtt-broker-prod`.
3. **Payload (minimal):** `productRaw`, `nfc`, `timestamp`; optional `orderId` nur wenn sinnvoll (nicht `"0"`).
4. **Nicht** über TXT-DPS-Firmware; **nicht** über osf-ui; **nicht** über Session Manager; Persistenz/SQL ist späterer Auswerte-Pfad, nicht Live-Quelle.
5. **Zielarchitektur:** langfristig kann **DSP** (statt CCU/Node-RED) dasselbe Topic befüllen; Bridge ist Übergang und kann wachsen. `osf/` ≠ nur osf-ui (Namespace für ORBIS-MQTT, vgl. DR-18).

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
- [ ] Image auf RPi laden + Compose-Service aktiv
- [ ] Optional: OSF-UI subscribed dasselbe Topic (Folge)

---
*Entscheidung getroffen von: Oliver Berger*
