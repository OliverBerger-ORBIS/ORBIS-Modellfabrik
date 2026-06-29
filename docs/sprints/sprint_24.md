# Sprint 24 – LOM-Day Vorbereitung & AI-HUB Datenerfassung

**Zeitraum:** 12.06.2026 – 25.06.2026 · **Status:** Abgeschlossen · **Vorheriger Sprint:** [Sprint 23](./sprint_23.md)

**Kurz:** Fortsetzung offener Integrationspunkte, Abschluss zentraler Sensor-Station-Hardwarearbeiten und Start des AI-HUB-Datenerfassungsprojekts (Object Detection/Tracking) als Vorbereitung fuer den LOM-Day.

---

## Externe Termine

| Datum | Event | Nutzen fuer OSF |
|--------|--------|----------------|
| — | — | Keine externen Termine im Sprintzeitraum 12.06–25.06 dokumentiert |

---

## Aufgaben (thematisch, mit Haken)

### ORBIS Feldbetrieb / Integrations-Fortsetzung (Carry-over aus Sprint 23)

- [ ] Datenpfad-Regel verbindlich dokumentieren und testen: ORBIS Live -> Broker `192.168.0.100`, Replay -> Broker `localhost`; Abweichungen als Troubleshooting-Checkliste erfassen.
- [ ] Lokalen Dashboard-Fall "keine orders" reproduzieren und Ursache dokumentieren (Ingest/Replay/Broker-Mapping/DB-Stand).
- [ ] Unterschiede localhost vs. RPi systematisch abarbeiten (insb. AGV-Erkennung/Anzeige auf RPi als Voraussetzung vor Overlay-Checks).

### Integration & Tests (Carry-over aus Sprint 23)

- [ ] **UI-Test-Framework (Fortsetzung):** von 2 Pilot-Tests zu stabiler Abdeckung kritischer Flows mit Tier A + Tier B Nachweisen ausbauen.
- [ ] **dsp/correlation/info** E2E (BLOCKED bis Team-Setup aktiv): End-to-End-Nachweis (Topic-Eingang + UI-Kontext) dokumentieren.
- [ ] **ccu/order/request** E2E (Ersatzauftrag nach Quality-Fail, BLOCKED bis Team-Setup aktiv): E2E-Nachweis mit klarer Ereigniskette dokumentieren.

### Backend & Deployment (Carry-over aus Sprint 23)

- [ ] Grafana-Dashboards ausbauen (fachliche Panels schaerfen, offene Visualisierungs-/Abnahmepunkte systematisch schliessen).
- [ ] Deployment vorbereiten: Grafana + Persistence-Stack auf DSP-Docker lauffaehig machen (neben local-dev als naechster Zielpfad).
- [ ] Session-Manager-Tags sauber namespacen (z. B. `session-manager-vX.Y.Z`) und Konvention in Release-Checkliste verankern.

### Sensor-Station / 3D-Druck & Mounting

- [x] Sensor-Station-Layout fuer Transport und Betrieb finalisiert: neue Grundplatte aufgebaut, Komponenten positioniert und verschraubt.
- [x] Halterung fuer 24V->12V DC/DC-Wandler inkl. Wago-Klemmen und Sicherung gedruckt und montiert.
- [x] Halterung fuer 12V-DC-Rundbuchse (Barrel Jack) gedruckt und integriert.
- [x] Verkabelungs-Qualitaetscheck Sensor-Board durchgefuehrt und dokumentiert (22.06.2026): 24V->12V-Pfad, Common Ground und Sensor-Pin-Remap auf Sketch v1.1.13 (SW-420 D3, DHT11 D2, Flame A2, MQ-2 A3) per Serial-Test verifiziert.
- [x] Vor-Ort Test ORBIS: Relais/Ampel-Funktion (Gruen/Gelb/Rot/Sirene) mit 12V-Lastpfad pruefen; Sensor-Station ist vor Ort angeschlossen.
- [x] 24V-Molex-Adapterkabel gefertigt und angeschlossen (23.06.2026): fischertechnik Molex 6-Pin auf Sensor-Station Molex 4-Pin (crimpen, Polaritaet geprueft, Sensor-Station in Betrieb genommen).
- [ ] Zielposition fuer `gwn6072m-mount` final entscheiden und verifizieren: ORBIS-Platte oder Platte der Charging-Station.
- [x] Dokumentation ergaenzen: mechanischer Aufbau, Druckteile, Befestigungspunkte und Montageablauf. **Nicht erforderlich** als detaillierte Repo-Doku; Einmal-Aktion ist abgeschlossen und wurde praktisch umgesetzt.

### AI-HUB Kooperation / Datenerfassung

- [x] Zusammenarbeit mit ORBIS AI-HUB (Dr. Abdul) fuer Object Detection und Object Tracking gestartet.
- [x] Datenbeitrag der OSF festgelegt: Konftel-20 Videodaten mit 60 FPS plus korrelierte NFC-Tag-Informationen aus MQTT.
- [x] Datenerhebung durchgefuehrt (25.06.2026): OD-Sessions aufgenommen und dem AI-HUB-Team zur Verfuegung gestellt.
- [x] Datenablage und Zuordnung dokumentieren (Dateinamen, Farbe, Order-Typ, NFC-Tag, MQTT-Korrelation pro Sequenz): MVP-Workflow im Session Manager Tab `Object Detection` eingefuehrt (Session-Ordner je Name, `manifest.json`, `meta_min.jsonl`, optional `events_full.log`, manuelle Videoablage).

### Praesentation / Video-Produktion

- [x] Praesentationsvideo Version 1 produziert (OBS Hero+2, MP4): vollstaendige OSF-Demo als durchgaengiges Video exportiert und fuer Messe-/Kundentermine ohne physisch verfuegbare OSF vorbereitet.

### Arduino Test-Follow-up

- [x] MQTT-E2E-Test erfolgreich (23.06.2026): Verifikation im ORBIS-Netz direkt ueber OSF Message-Monitor; Arduino-Sketch mit MQTT aktiv und Topics empfangen.

### Track&Trace / APS (Carry-over aus Sprint 23)

- [ ] APS-Erweiterung: neue NFC-IDs generierbar machen, damit Track&Trace nicht dauerhaft auf denselben NFCs basiert.

### Blog & Organisation (Carry-over aus Sprint 23)

- [ ] Blog: Reviews A1, A2, A3
- [ ] Azure DevOps: Repo/Boards von GitHub

### Sprint-Wechsel (am Ende des Sprints abarbeiten)

- [x] Sprint 24: Status Abgeschlossen, Datum
- [x] Sprint 25 angelegt, offene `[ ]` uebernommen
- [x] PROJECT_STATUS / Roadmap kurz

---

## Retrospektive

- Datenerhebung fuer Object Detection erfolgreich gestartet; Sessions an AI-HUB uebergeben.
- Praesentationsvideo V1 (OBS Hero+2) ist verfuegbar und bildet eine lauffaehige Offline-Demo ab.
- Offene Integrations-/Deployment-Themen wurden bewusst in den Folge-Sprint uebernommen.

---

## Später (Backlog)

- Router-Variante / Mounting-Strategie fuer Folgehardware konsolidieren (Stabilitaet, Servicezugang, Kabelfuehrung).

---

## Links

- [Sprint 23](sprint_23.md) · [PROJECT_STATUS.md](../PROJECT_STATUS.md) · [sprints_README.md](sprints_README.md)

---

*Stand: 29.06.2026* · Doku-Workflow: [sprints_README.md](sprints_README.md)
