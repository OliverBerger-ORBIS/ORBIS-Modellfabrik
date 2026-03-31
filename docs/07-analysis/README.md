# 07-Analysis

Sprint-bezogene und projektweite Analysen für OSF.

> **Archiv (2026-02):** Obsolete empirische Analysen → [analysis-obsolete-2026](../archive/analysis-obsolete-2026/)  
> Grund: Fischertechnik-Doku und CCU-Source sind maßgeblich.

---

## Test Coverage & Build

- [test-coverage-status.md](test-coverage-status.md) – Aktuelle Coverage-Metriken, Fortschritt
- [test-coverage-summary.md](test-coverage-summary.md) – Zusammenfassung abgeschlossener Phasen
- [build-commands-guide.md](build-commands-guide.md) – Build-Befehle für osf-ui (Production, Development, GitHub Pages)

---

## MQTT, Registry, Topics

- [publish-buttons-analysis.md](publish-buttons-analysis.md) – OSF Buttons vs. OMF2, MQTT-Topics
- [ccu-backend-mqtt-orchestration.md](ccu-backend-mqtt-orchestration.md) – CCU-Backend MQTT
- [REGISTRY_TOPIC_STRUCTURE.md](REGISTRY_TOPIC_STRUCTURE.md) – Topic-Struktur
- [TOPIC_SCHEMA_CORRELATION.md](TOPIC_SCHEMA_CORRELATION.md) – Schema-Korrelation
- [topic-naming-convention-analysis.md](topic-naming-convention-analysis.md) – Naming Conventions

---

## Order / Track & Trace

- [production-order-analysis-results.md](production-order-analysis-results.md) – Order-Workflow aus Session-Analyse, OSF Order Manager Anforderungen, CCU-Backend-Analyse (referenziert von 13-track-trace-architecture)
- [order-agv-mapping-without-mod3-2026-03.md](order-agv-mapping-without-mod3-2026-03.md) – Order↔AGV-Zuordnung ohne Mod-3-Wiederherstellung (Optionen, Empfehlung: Ableitung aus fts/order)

---

## Hardware / FTS / AGV

**Referenz / Pflege:** [second-agv-2026-03.md](second-agv-2026-03.md) (Konsolidat), [fts-navigation-how-it-works-2026-03.md](fts-navigation-how-it-works-2026-03.md) (Navigation, manuell → HBW / clearLoadHandler).

- [second-agv-2026-03.md](second-agv-2026-03.md) – Zweites AGV (leJ4), Dual-UI, Gateway `fts$`, Layout `fts[]`; Sprint 17→18
- [fts-navigation-how-it-works-2026-03.md](fts-navigation-how-it-works-2026-03.md) – FTS/AGV-Navigation (CCU, Topics, osf-ui)
- [two-agvs-mixed-session-data-inventory-2026-03.md](two-agvs-mixed-session-data-inventory-2026-03.md) – two-agvs-mixed: Topic-Inventar, jp93→leJ4 (empirisch)
- [order-agv-mapping-without-mod3-2026-03.md](order-agv-mapping-without-mod3-2026-03.md) – Order↔AGV ohne Mod-3 in Steps (`fts/order`-Ableitung)
- [agv-position-after-order-completion-2026-03.md](agv-position-after-order-completion-2026-03.md) – AGV-Endposition nach Orders (Code vs. Session; **Randbedingung:** leere Queue)
- [agv-overlay-rendering-differences-2026-03.md](agv-overlay-rendering-differences-2026-03.md) – RPi vs. localhost Overlay (bekannt, ggf. ungelöst)
- [agv-order-tab-color-analysis-2026-03.md](agv-order-tab-color-analysis-2026-03.md) – **historisch** → maßgeblich [DR-24](../03-decision-records/24-shopfloor-highlight-colors.md)
- [order-tab-active-module-highlight-analysis-2026-03.md](order-tab-active-module-highlight-analysis-2026-03.md) – **historisch** → [DR-24](../03-decision-records/24-shopfloor-highlight-colors.md)

**Tiefergehend (Session-Forensik März 2026, teils `jp93`):** für CCU/TXT/MES-Stillsitze, nicht als aktuelle UI-Spezifikation lesen — Serien heute **leJ4**.

- [two-agvs-mixed-event-chain-fischertechnik-2026-03.md](two-agvs-mixed-event-chain-fischertechnik-2026-03.md) – Ursachenkette DPS busy / parallele Orders
- [two-agvs-mixed-agv2-dps-busy-2026-03.md](two-agvs-mixed-agv2-dps-busy-2026-03.md) – DROP FINISHED / State-Serial NodeRed vs. TXT
- [agv-2-mixed-standstill-2026-03.md](agv-2-mixed-standstill-2026-03.md) – agv-2-mixed Stillstand
- [storage-order-rejection-two-agvs-2026-03.md](storage-order-rejection-two-agvs-2026-03.md) – Storage UNKNOWN / HBW loads leer

---

## Weitere Analysen

- **SVG-Diagramme (Doku):** [OSF-UI: SVG label text & line breaks](../04-howto/osf-ui-svg-label-text-conventions.md) — drei Kontexte (DSP-Architecture, DSP-Animation, UC-01); visueller Check; Phase 2: gemeinsame Utils.
- **Konvention (Doku):** [DR-26 – UTC-Zeitstempel (ms)](../03-decision-records/26-utc-iso-timestamp-ms-convention.md) — OSF/Session Manager; CCU/TXT unverändert.
- [publish-buttons-tests-summary.md](publish-buttons-tests-summary.md) – Publish-Button Tests
- [AS-IS-FISCHERTECHNIK-COMPARISON.md](AS-IS-FISCHERTECHNIK-COMPARISON.md) – Abgleich AS-IS vs. Fischertechnik
- [INTEGRATIONS-VENDOR-ANALYSIS.md](INTEGRATIONS-VENDOR-ANALYSIS.md) – integrations vs. vendor
- [SESSION-QOS-RETAIN-ANALYSIS-20260303.md](SESSION-QOS-RETAIN-ANALYSIS-20260303.md) – QoS/Retain empirische Verifizierung (03.03.2026)
- [SESSION-RECORDINGS-USAGE-AND-PRELOAD-AUDIT.md](SESSION-RECORDINGS-USAGE-AND-PRELOAD-AUDIT.md) – Session-Verwendung, start-osf Default, Preload-Strategie
- [ccu-quality-fail-behaviour-2026-03.md](ccu-quality-fail-behaviour-2026-03.md) – CCU Quality-Fail: Ersatzauftrag vs. Order ERROR (Sprint 17, temporär)
