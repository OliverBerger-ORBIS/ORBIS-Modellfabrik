# Sprint 26 – NFC-Tags, Use-Case-Darstellung & Grafana Dashboard

**Zeitraum:** 10.07.2026 – 23.07.2026 · **Status:** Abgeschlossen · **Vorheriger Sprint:** [Sprint 25](./sprint_25.md) · **Nächster Sprint:** [Sprint 27](./sprint_27.md)

**Kurz:** NFC-Tag-Erweiterung fuer Track&Trace, **Landscape/Hero-Praesentationsprofile** fuer Use-Case-/DSP-Diagramme (Browser-Zoom Desktop 2/3, Diagramm-Skalierung), Grafana-Dashboard/Persistence-Datenpfad und Modus-A-Replay-Verifikation.

---

## Externe Termine & Outreach

*Kundentermine, Demos und Blog-Artikel — externe Wirkung / Umsatz-relevante OSF-Nutzung. Bei Sprint-Abschluss auch in [PROJECT_STATUS](../PROJECT_STATUS.md) → Spalte **Externe Events**.*

| Datum | Event | Nutzen fuer OSF |
|--------|--------|----------------|
| **19.06.2026** | **Blog A1** veröffentlicht — [Skalierbare Smart Factory](https://www.orbis-group.com/de-de/blog/branchen/manufacturing/skalierbare-smart-factory/) | Storytelling-Serie gestartet (Basis A2–A4); Marketing/Lead-Unterstützung *(Sprint 24)* |
| **14.07.2026** | **Interner Probelauf** Windows-Desktop/OBS + MES/PT (Musashi → 14.08.) | Dress rehearsal statt Kundentermin — Probelauf 14.07. + Live-Test 15.07. abgeschlossen |
| **16.07.2026** | **Blog A2 Review** (Track & Trace als konkreter Anwendungsfall) | Review erfolgt; Veröffentlichung **23.07.2026** |
| **23.07.2026** | **Blog A2** veröffentlicht — [Track und Trace in der Fertigung](https://www.orbis-group.com/de-de/blog/branchen/manufacturing/track-und-trace-in-der-fertigung/) | Storytelling-Serie A2 live; Marketing/Lead-Unterstützung |
| **geplant** | **Hochschulkooperation** — Kshitiz Bohara (Doktorand, Uni Magdeburg): GenAI / Agentic AI im Umfeld SmartFactory, MES, DSP | Möglicher erster Use Case: semantisch gestützte Analyse von Track-&-Trace- und Qualitätsereignissen. **Offen:** strategische Abstimmung innerhalb ORBIS nach dem ersten Kennenlerngespräch |
| **14.08.2026** | **Kundentermin Musashi** (verschoben von 14.07.2026) | Erstverifikation Router-/Netzwerk-Setup und Windows-Desktop-Praesentation (Follow-up LOM-Day) |

---

## Aufgaben (thematisch, mit Haken)

### Router / Netzwerk-Setup

- [x] **GL.iNet-Router-Mount (DPS-Station):** 3D-Druck erstellt und passgenau an der **DPS-Station** eingebaut — ersetzt den originalen **FT-Router** vor Ort. *(14.07.2026)*
- [x] **Office-Tower 3D-Druck (23.07.2026):** Gehäuse für **Proxmox**, **TP-Link Omada** und **GL.iNet grau** — fertiggestellt; repräsentiert die **ORBIS-DSP-Edge**-Komponente visuell am Shopfloor.
- [x] **Netzwerk-Topologie — Omada-Port-Pinout + Fotos (21.07.2026):** [How-to](../04-howto/setup/orbis-shopfloor-network-topology.md) — P1 grau LTE, P3 weiß GL.iNet WAN, P4 FT-Switch, P5 Proxmox; Fotos `docs/assets/setup/network/`. Ping FT-LAN OK (Mac `.189`).
- [ ] **Netzwerk-Topologie/Verkabelung (Rest):** ORBIS-LAN-Adressliste + MES-Pfad mit Netzwerk-Kollegen (**nur mit ORBIS-VPN testbar**); Omada Admin-URL/Modell; ggf. HTML neu exportieren. *(Sprint 26)*
- [x] **Netzwerk-Topologie — DSP Edge + WLAN-Kopplung (17.07.2026):** Proxmox `.200:8006` + VE `.201`; Dual-SSID Demo-WLAN im FT-LAN-Subnetz.
- [x] **OSF External Links auf RPi deployen (21.07.2026):** Mit OSF-UI **v1.1.9** — `dspEdgeUrl` = `https://192.168.0.200:8006` in Container `osf-ui-prod` (en/de/fr `assets/config/external-links.json`). Bookmarks `SmartFactory.html` bereits angepasst.
- *Rollen: GL.iNet weiß = DPS/FT-Gateway; GL.iNet grau = LTE→Omada WAN; Omada = WLAN + Port-Hub; Proxmox = DSP Edge im FT-LAN.*

### Praesentation (Windows-Desktops / OSF-UI)

- [x] **OSF-UI Praesentation Landscape/Hero (Desktop 2 + 3):** UC **Landscape**, DSP **Hero** — verifiziert 14.07.2026 @ 1920×1200; Checkliste [windows-desktops-teams-obs-setup-checklist.md](../04-howto/presentation/windows-desktops-teams-obs-setup-checklist.md).
- [x] **Windows-Desktop-/OBS-Setup (Probelauf 14.07.2026):** virtuelle Desktops, OBS-Kamera, Tab-Gruppen inkl. **MES MD1** und **PT MD1** — grundsaetzlich lauffaehig.
- [x] **Praesentations-Setup Live-Test (15.07.2026):** Ablauf nach aktualisierter Checkliste — Shopfloor, Konftel-20/OBS (zwei Previews), Tab-Gruppen **OSF-RPi** + **MES** + **DSP**, Anzeige **Duplizieren**, Desktop-Verteilung (`Win + Ctrl + ←/→`), Preset-Kurztest — erfolgreich.
- [x] **Praesentations-Doku** und SmartFactory Favoriten im Azure DevOPs Projekt

### Track&Trace / NFC-Tags

- [x] **NFC B-soft — `.ft`-Änderung (17.07.2026):** Arbeitskopie `integrations/TXT-DPS/archives/FF_DPS_24V_osf_nfc.ft` — Blockly in `lib/VGR` (`handle_NFC` logische ID, Ausgang nur Tag-Present); Baseline `FF_DPS_24V.ft` + weitere TXT-Archives (AIQS/CGW/FTS) aus GitLab. Plan [nfc-logical-id-b-soft-plan-2026-07.md](../07-analysis/nfc-logical-id-b-soft-plan-2026-07.md); Workflow [txt-controller-deployment.md](../04-howto/txt-controller-deployment.md). *(Ursprung: Sprint 22)*
- [x] **NFC B-soft — Deploy + Live-Test (21.07.2026):** `FF_DPS_24V_osf_nfc.ft` auf DPS-TXT (.186) Deploy + Autostart. Test A OK (gleicher weißer Tag → zwei logische IDs); Test B OK (Ausgang ohne `NFC_workpieceId_mismatch`). Plan-Doku in `docs/07-analysis/` nach Sprint-Closeout löschen. *(Ursprung: Sprint 22)*
- [x] **Track&Trace Live Demo UX (21.07.2026):** Landscape-/Viewport-Fit nur für Concept; Live-Panel `overflow-y: auto`; kompakte Sections (NFC-Suche rechts neben Überschrift; Werkstückfarbe-Label + Chips in einer Zeile; reduzierte Toolbar).
- [ ] **Track&Trace Live Demo Inhalt (Multi-Order / Publisher / Zeitstrahl):** Auftragskontext STORAGE+PRODUCTION; Event-Publisher (FTS vs. Modul); Sub-Order-Gruppen nach Timestamp statt nur Sub-Order-Nr. Phase 1: A1+C1+B1; Phase 2 optional: FTS-Stations-Synthese abschalten (B3). Arbeitsdoku [track-trace-live-content-fix-2026-07.md](../07-analysis/track-trace-live-content-fix-2026-07.md). **HomeOffice/Replay** ausreichend. *(21.07.2026, Feldbefund)*
- *Wozu: Track&Trace-Demos und Kundentermine mit frischen Werkstueck-Identitaeten statt wiederholter NFCs.*
- *Hinweis Demo: Capture läuft in Live/Replay nach MQTT-Connect auch ohne offenen Tab; Header-Refresh leert die Historie — dazwischen nicht unnötig refreshen.*)

### Grafana Dashboard

- [ ] **Modus A (Replay + Session):** Grafana `localhost:3000` mit Session-Replay erneut pruefen — Orders/Daten sichtbar; Abweichungen in Troubleshooting dokumentieren. *(Ursprung: Sprint 22; Nachfolger „keine orders“; siehe [runtime-modes-matrix.md](../04-howto/helper_apps/session-manager/runtime-modes-matrix.md))*
- [ ] Grafana-Dashboards ausbauen (fachliche Panels schaerfen, offene Visualisierungs-/Abnahmepunkte systematisch schliessen). *(Ursprung: Sprint 22)*
- [ ] Deployment vorbereiten: Grafana + Persistence-Stack auf DSP-Docker lauffaehig machen (neben local-dev als naechster Zielpfad). *(Ursprung: Sprint 22)*
- [ ] **Track&Trace Persistenz (Option B):** UI-Historie bleibt session-/RAM-scoped; längere NFC-Spuren über Edge/Grafana (`osf-edge-persistence`, [DR-28](../03-decision-records/28-edge-persistence-stack-and-metrics-model.md)) — kein Browser-localStorage. Größere Folgeaufgabe, voraussichtlich **Sprint 27**. *(Entscheidung 21.07.2026)*

### ORBIS Feldbetrieb / Integrations-Fortsetzung

- [x] **RPi OSF-UI v1.1.8 deployen (15.07.2026):** `npm run docker:osf-ui:deploy -- ff22@192.168.0.100` — Container `orbis-osf-ui:1.1.8`, HTTP `:8080` 200 OK.
- [x] **RPi OSF-UI v1.1.9 deployen (21.07.2026):** Track&Trace Live Demo UX + Sprint-26-Doku — `npm run docker:osf-ui:deploy -- ff22@192.168.0.100` — Container `orbis-osf-ui:1.1.9`, HTTP `:8080` OK.
- [x] **Shopfloor CELL_* als Serial (Fix in Code, v1.1.10):** Layout-Load über `ShopfloorLayoutService`/`baseHref`; Auswahl löst Hardware-Serial auf; kein Persistieren von `CELL_*`. Unit-Tests grün. **Verifikation RPi OK (21.07.2026):** Hard-Reload → Modul-Klick zeigt `SVR…`, nicht `CELL_*`.
- [x] **RPi OSF-UI v1.1.10 deployen (21.07.2026):** Shopfloor-Layout-/Serial-Fix — `npm run docker:osf-ui:deploy -- ff22@192.168.0.100` — Container `orbis-osf-ui:1.1.10`, HTTP `:8080` OK; Live-Test Serial-Anzeige OK.
- [x] Unterschiede zwischen localhost und RPi systematisch abarbeiten (insb. AGV-Erkennung/Anzeige auf RPi als Voraussetzung vor Overlay-Checks). **Not necessary** (16.07.2026): Präsentations-Setup-Checks — AGV-Darstellung/Overlay präsentationsfähig; LH↔RPi-/Browser-Unterschiede vorerst kein Prioritätsthema. *(Ursprung: Sprint 22)*
- [ ] **Kontrolle FTS Nr. 2 (RoboPro-Schnittstellen-Test):** Überprüfung per RoboPro-Schnittstellen-Test — Befund: **Kabelbruch oder Motor defekt**; weitere Prüfungen stehen noch an. **Erledigt dabei:** Vorgehen für RoboPro-Schnittstellen-Tests erfolgreich durchgeführt; TXT-Projekte lokal unter `integrations/` abgelegt (u. a. `TXT-FTS` Archives/Workspaces). *(23.07.2026)*

### Integration & Tests

- [ ] **UI-Test-Framework (Fortsetzung):** von 2 Pilot-Tests zu stabiler Abdeckung kritischer Flows mit Tier A + Tier B Nachweisen ausbauen. *(Ursprung: Sprint 21)*
- [ ] **dsp/correlation/info** E2E (BLOCKED bis Team-Setup aktiv): End-to-End-Nachweis (Topic-Eingang + UI-Kontext) dokumentieren. *(Ursprung: Sprint 18)*
- [ ] **ccu/order/request** E2E (Ersatzauftrag nach Quality-Fail, BLOCKED bis Team-Setup aktiv): E2E-Nachweis mit klarer Ereigniskette dokumentieren. *(Ursprung: Sprint 18)*

### Blog & Organisation

- [x] **Blog A1 veröffentlicht (19.06.2026):** [Skalierbare Smart Factory](https://www.orbis-group.com/de-de/blog/branchen/manufacturing/skalierbare-smart-factory/) — siehe auch Tabelle **Externe Termine & Outreach**. *(Ursprung: Sprint 24; Basis für A2, A3 und A4)*
- [x] **Blog A2 Review (16.07.2026):** Track & Trace als konkreter Anwendungsfall — Review erfolgt. *(Outreach-Tabelle)*
- [x] **Blog A2 veröffentlicht (23.07.2026):** [Track und Trace in der Fertigung](https://www.orbis-group.com/de-de/blog/branchen/manufacturing/track-und-trace-in-der-fertigung/)
- [ ] Blog: Review A3 *(Von Daten zu belastbaren KPIs)*
- [ ] Blog: Review A4 *(Von Erkenntnissen zu Aktionen)*
- [ ] Azure DevOps: Repo/Boards von GitHub *(Ursprung: Sprint 19)*

### Sprint-Wechsel (am Ende des Sprints abarbeiten)

- [x] Sprint 26: Status Abgeschlossen, Datum (23.07.2026)
- [x] Sprint 27 anlegen, offene `[ ]` uebernehmen (23.07.2026) — Fokus Grafana + Track&Trace
- [x] PROJECT_STATUS / Roadmap kurz (23.07.2026)

---

## Links

- [Sprint 25](sprint_25.md) · [Sprint 27](sprint_27.md) · [PROJECT_STATUS.md](../PROJECT_STATUS.md) · [sprints_README.md](sprints_README.md)

---

*Stand: 23.07.2026* · Doku-Workflow: [sprints_README.md](sprints_README.md)
