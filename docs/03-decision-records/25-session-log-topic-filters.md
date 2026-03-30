# Decision Record: Session-Logs für Analysen & optionale Topic-Filter im Session Manager

**Datum:** 2026-03-30  
**Status:** Accepted  
**Kontext:** Session-Logs unter `data/osf-data/sessions/` sind wichtige Grundlage für Replay, Auswertungen und KI-gestützte Analysen. Zuvor waren große Log-/Session-Pfade teils in `.cursorignore` — damit waren Auswertungen im IDE-Kontext erschwert. Parallel produzieren **Arduino-Multisensor-**, **BME680-** und **Kamera-**Topics hohes Volumen, das für die meisten OSF-/CCU-/AGV-Analysen wenig Mehrwert bringt.

> **Vorgehensweise:** [README – Vorgehensweise](README.md#vorgehensweise-wann-wird-ein-decision-record-erstellt)

---

## Entscheidung

1. **Cursor / Repository:** Session-Logs und typische Aufzeichnungsdateien (`data/osf-data/sessions/`, projektinterne `*.log` wo sinnvoll) **nicht** in `.cursorignore` aufnehmen, um **Auswertung und Agent-Unarbeitung** zu erlauben. Ausnahmen bleiben rein technische Pfade (z. B. `node_modules/`, Build-Artefakte) wie in `.cursorignore` dokumentiert.
2. **Neue Aufnahmen:** Bewusst **neue Sessions im Zwei-AGV-/Mixed-Betrieb** erzeugen und ablegen, sobald Messe- oder Shopfloor-Setup es zulässt — Ergänzung zu Mock-Fixtures.
3. **Session Manager (Umsetzung folgt):** Einstellung **„Analyse-Aufnahme“** bzw. Topic-**Ausschlussliste** (Preset oder editierbare Muster), sodass beim **Record** mindestens optional unterdrückt werden können:
   - **Arduino-Sensordaten** nach Topic-Schema aus [DR-18](18-osf-extensions-ip-and-mqtt-topics.md) (`osf/arduino/…`)
   - **BME680** am TXT: `/j1/txt/1/i/bme680`
   - **Kamera** am TXT: `/j1/txt/1/i/cam` (JPEG-Payload, dominiert oft das Logvolumen — vgl. u. a. [two-agvs-mixed-session-data-inventory-2026-03.md](../07-analysis/two-agvs-mixed-session-data-inventory-2026-03.md))

   Technisch: Nachricht mit passendem Topic **nicht** in die Session-Zeilenausgabe schreiben (oder konfigurierbar „nur Metadaten“), ohne `subscribe`/`on_connect`-Invarianten des MQTT-Clients zu brechen ([`.cursorrules`](../../.cursorrules) — Session Recorder).

## Alternativen

- **Nur nachträglich filtern (Script):** verworfen — spart nicht die Aufnahmezeit und erfordert trotzdem große Rohdateien.
- **Broker-seitige ACL/Filter:** verworfen — Broker ist geteilt; Shopfloor- und OSF-Clients brauchen Topics weiterhin.

## Konsequenzen

- **Positiv:** Kleinere, fokussiertere Logfiles bei aktiviertem Ausschluss; Agents können Logs weiterhin vollständig einlesen.
- **Negativ:** Ohne Filter weiterhin große Dateien; bei Ausschluss fehlen Spuren für reine Sensor-/Kamera-Debugs in derselben Datei.
- **Risiken:** Fehlkonfiguration der Ausschlussmuster — Muss über UI/Preset und Kurzdoku im Session-Manager README abfedern.

## Implementierung

- [ ] Session Manager: UI-Option (Preset „Analyse (ohne Sensor-Cam-Noise)“) + persistente Konfiguration
- [ ] Session Manager: Filter im Write-Pfad des Recorders (Tests mit Mock-Messages)
- [ ] `session_manager/README.md`: kurze How-to-Sektion zu Preset und Topic-Liste
- [ ] Verweis von Sprint/Task oder Backlog auf dieses DR nach Umsetzung abhaken

---
*Entscheidung dokumentiert für OSF / ORBIS Modellfabrik.*
