# Sprint 27 – Grafana-Dashboard-Analyse & Track&Trace

**Zeitraum:** 24.07.2026 – 06.08.2026 · **Status:** Laufend · **Vorheriger Sprint:** [Sprint 26](./sprint_26.md)

**Kurz:** Fokus **Grafana-Dashboard-Analyse** (Modus A / Panels / Persistenz-Pfad) in Kombination mit offenen **Track&Trace**-Tasks (Live-Demo Inhalt, Edge-Persistenz Option B); Carry-over Netzwerk, FTS Nr. 2, Blog A3/A4 und Integrations-Nachweise.

---

## Externe Termine & Outreach

*Kundentermine, Demos und Blog-Artikel — externe Wirkung / Umsatz-relevante OSF-Nutzung. Bei Sprint-Abschluss auch in [PROJECT_STATUS](../PROJECT_STATUS.md) → Spalte **Externe Events**.*

| Datum | Event | Nutzen fuer OSF |
|--------|--------|----------------|
| **23.07.2026** | **Blog A2** veröffentlicht — [Track und Trace in der Fertigung](https://www.orbis-group.com/de-de/blog/branchen/manufacturing/track-und-trace-in-der-fertigung/) | Storytelling-Serie A2 live *(Sprint 26)* |
| **geplant** | **Hochschulkooperation** — Kshitiz Bohara (Doktorand, Uni Magdeburg): GenAI / Agentic AI im Umfeld SmartFactory, MES, DSP | Möglicher erster Use Case: semantisch gestützte Analyse von Track-&-Trace- und Qualitätsereignissen. **Offen:** strategische Abstimmung innerhalb ORBIS nach dem ersten Kennenlerngespräch |
| **14.08.2026** | **Kundentermin Musashi** | Erstverifikation Router-/Netzwerk-Setup und Windows-Desktop-Praesentation (Follow-up LOM-Day; verschoben von 14.07.) |

---

## Aufgaben (thematisch, mit Haken)

### Grafana Dashboard *(Fokus)*

- [ ] **Modus A (Replay + Session):** Grafana `localhost:3000` mit Session-Replay erneut pruefen — Orders/Daten sichtbar; Abweichungen in Troubleshooting dokumentieren. *(Ursprung: Sprint 22; Nachfolger „keine orders“; siehe [runtime-modes-matrix.md](../04-howto/helper_apps/session-manager/runtime-modes-matrix.md))*
- [ ] Grafana-Dashboards ausbauen (fachliche Panels schaerfen, offene Visualisierungs-/Abnahmepunkte systematisch schliessen). *(Ursprung: Sprint 22)*
- [ ] Deployment vorbereiten: Grafana + Persistence-Stack auf DSP-Docker lauffaehig machen (neben local-dev als naechster Zielpfad). *(Ursprung: Sprint 22)*
- [ ] **Track&Trace Persistenz (Option B):** UI-Historie bleibt session-/RAM-scoped; längere NFC-Spuren über Edge/Grafana (`osf-edge-persistence`, [DR-28](../03-decision-records/28-edge-persistence-stack-and-metrics-model.md)) — kein Browser-localStorage. *(Entscheidung 21.07.2026; Ursprung: Sprint 26)*

### Track&Trace *(Fokus)*

- [ ] **Track&Trace Live Demo Inhalt (Multi-Order / Publisher / Zeitstrahl):** Auftragskontext STORAGE+PRODUCTION; Event-Publisher (FTS vs. Modul); Sub-Order-Gruppen nach Timestamp statt nur Sub-Order-Nr. Phase 1: A1+C1+B1; Phase 2 optional: FTS-Stations-Synthese abschalten (B3). Arbeitsdoku [track-trace-live-content-fix-2026-07.md](../07-analysis/track-trace-live-content-fix-2026-07.md). **HomeOffice/Replay** ausreichend. *(21.07.2026, Feldbefund; Ursprung: Sprint 26)*
- *Hinweis Demo: Capture läuft in Live/Replay nach MQTT-Connect auch ohne offenen Tab; Header-Refresh leert die Historie — dazwischen nicht unnötig refreshen.*

### Router / Netzwerk-Setup

- [ ] **Netzwerk-Topologie/Verkabelung (Rest):** ORBIS-LAN-Adressliste + MES-Pfad mit Netzwerk-Kollegen (**nur mit ORBIS-VPN testbar**); Omada Admin-URL/Modell; ggf. HTML neu exportieren. *(Ursprung: Sprint 26)*
- *Rollen: GL.iNet weiß = DPS/FT-Gateway; GL.iNet grau = LTE→Omada WAN; Omada = WLAN + Port-Hub; Proxmox = DSP Edge im FT-LAN. How-to: [orbis-shopfloor-network-topology.md](../04-howto/setup/orbis-shopfloor-network-topology.md).*

### ORBIS Feldbetrieb / Hardware

- [ ] **Kontrolle FTS Nr. 2 (Folgeprüfungen):** Weiterer Diagnose nach RoboPro-Schnittstellen-Test — Befund bisher **Kabelbruch oder Motor defekt**. *(23.07.2026; Ursprung: Sprint 26; TXT-Projekte lokal unter `integrations/`)*

### Integration & Tests

- [ ] **UI-Test-Framework (Fortsetzung):** von 2 Pilot-Tests zu stabiler Abdeckung kritischer Flows mit Tier A + Tier B Nachweisen ausbauen. *(Ursprung: Sprint 21)*
- [ ] **dsp/correlation/info** E2E (BLOCKED bis Team-Setup aktiv): End-to-End-Nachweis (Topic-Eingang + UI-Kontext) dokumentieren. *(Ursprung: Sprint 18)*
- [ ] **ccu/order/request** E2E (Ersatzauftrag nach Quality-Fail, BLOCKED bis Team-Setup aktiv): E2E-Nachweis mit klarer Ereigniskette dokumentieren. *(Ursprung: Sprint 18)*

### Blog & Organisation

- [ ] Blog: Review A3 *(Von Daten zu belastbaren KPIs)* *(Ursprung: Sprint 19 / 26)*
- [ ] Blog: Review A4 *(Von Erkenntnissen zu Aktionen)* *(Ursprung: Sprint 19 / 26)*
- [ ] Azure DevOps: Repo/Boards von GitHub *(Ursprung: Sprint 19)*

### Sprint-Wechsel (am Ende des Sprints abarbeiten)

- [ ] Sprint 27: Status Abgeschlossen, Datum *(Ursprung: Sprint 27)*
- [ ] Sprint 28 anlegen, offene `[ ]` uebernehmen *(Ursprung: Sprint 27)*
- [ ] PROJECT_STATUS / Roadmap kurz *(Ursprung: Sprint 27)*

---

## Links

- [Sprint 26](sprint_26.md) · [PROJECT_STATUS.md](../PROJECT_STATUS.md) · [sprints_README.md](sprints_README.md)

---

*Stand: 23.07.2026* · Doku-Workflow: [sprints_README.md](sprints_README.md)
