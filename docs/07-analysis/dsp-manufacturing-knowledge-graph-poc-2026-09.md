# DSP × Uni Magdeburg — Manufacturing Knowledge Graph PoC (Management Summary)

**Stand:** 2026-09-03  
**Kontext:** Kooperation Uni Magdeburg (Dr. Reggelin / **Kshitiz**); Deep-Dive SB **21./22.09.2026**  
**Sprint:** [sprint_30.md](../sprints/sprint_30.md) — Roadmap-Planung (Konzept)

---

## Idee

DSP wird um eine **KI-gestützte semantische Wissensschicht** auf Basis eines **Manufacturing Knowledge Graph** ergänzt. DSP bleibt die zentrale Integrations- und Prozessschicht. Der Knowledge Graph verknüpft die über DSP verfügbaren Informationen aus **Shopfloor, MES, SAP und Sensorik**, sodass sie nachvollziehbar durch ein **LLM** abgefragt und ausgewertet werden können.

---

## Strategischer Vorteil für ORBIS und DSP

- DSP wird als zentrale Daten- und Integrationsbasis für **vertrauenswürdige Shopfloor-AI** positioniert.
- Vorhandene DSP-Daten erhalten durch semantische Verknüpfung und natürlichsprachliche Abfragen einen zusätzlichen, sichtbaren Nutzen.
- **Track & Trace** kann perspektivisch von der reinen Ereignis-/Genealogiedarstellung zur **erklärbaren Ursachenanalyse** erweitert werden.
- Der Ansatz ist **additiv**: Der PoC greift zunächst nur **lesend** auf Daten zu und verändert weder DSP noch operative Prozesse.
- Die **ORBIS SmartFactory** ermöglicht einen kontrollierten PoC **ohne Kundendaten**. Bei erfolgreichem Nachweis kann der Ansatz später gemeinsam mit einem geeigneten Kunden unter realen Bedingungen validiert werden.
- **Kshitiz** übernimmt einen wesentlichen Teil der technischen Entwicklung. ORBIS stellt vor allem fachlichen Kontext, definierte Datenzugänge und technische Ansprechpartner bereit.

---

## Fazit

Mit überschaubarem Risiko und begrenztem Anfangsaufwand prüfen, wie DSP zur Plattform für nachvollziehbare **GenAI-** und **Agentic-AI**-Anwendungen im Shopfloor weiterentwickelt bzw. positioniert werden kann.

---

**Datenkante (04.09.2026):** Dieselbe Hub-DB `osf_edge` auf `.201` wie Grafana und künftige DSP-Use-Case-Demos; APS-Tabs sind **kein** PoC-Zugang. Details: [dsp-tab-persistence-use-cases-2026-09.md](dsp-tab-persistence-use-cases-2026-09.md).

## Nächste Schritte (Sprint 30 — Konzept)

- [ ] Kurzfassung für Deep-Dive SB (Stakeholder / DSP-Team)
- [x] Datenquellen OSF/Edge (MQTT, Persistenz `.201`, Grafana) vs. DSP-Scope abgrenzen — APS = MQTT-Live; DSP-Hub-DB = Historie; KG lesend darauf
- [x] Lesender PoC-Schnitt: zuerst `shopfloor_event` + `workpiece` + `env_sensor_snapshot`; MQTT nur für Realtime-Alarm (UC-07-analog)
- [ ] Rollen: Kshitiz (Technik) / ORBIS (Fachkontext, Zugang, Ansprechpartner)
