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

- [agv-position-after-order-completion-2026-03.md](agv-position-after-order-completion-2026-03.md) – AGV-Position nach Production-/Storage-Abschluss und Quality-Fail (analytisch + empirisch)
- [fts-navigation-how-it-works-2026-03.md](fts-navigation-how-it-works-2026-03.md) – FTS-Navigation: Wer erstellt NAV, Topics, Payloads, osf-ui manuelle NAV
- [second-agv-2026-03.md](second-agv-2026-03.md) – Zweites AGV (leJ4) – Implementierung & Referenz (Sprint 17)
- [two-agvs-mixed-session-data-inventory-2026-03.md](two-agvs-mixed-session-data-inventory-2026-03.md) – two-agvs-mixed: empirische Topics/Felder, Serial jp93→leJ4
- [agv-overlay-rendering-differences-2026-03.md](agv-overlay-rendering-differences-2026-03.md) – AGV-Overlay: Rendering-Unterschiede Mac vs. RPi (z-index, filter, Cache)
- [agv-order-tab-color-analysis-2026-03.md](agv-order-tab-color-analysis-2026-03.md) – AGV-Darstellung ORDER-Tab vs. AGV-Tab (→ DR-24)
- [order-tab-active-module-highlight-analysis-2026-03.md](order-tab-active-module-highlight-analysis-2026-03.md) – ORDER-Tab: Aktives Modul blau vs. Grün (→ DR-24)

---

## Weitere Analysen

- [publish-buttons-tests-summary.md](publish-buttons-tests-summary.md) – Publish-Button Tests
- [AS-IS-FISCHERTECHNIK-COMPARISON.md](AS-IS-FISCHERTECHNIK-COMPARISON.md) – Abgleich AS-IS vs. Fischertechnik
- [INTEGRATIONS-VENDOR-ANALYSIS.md](INTEGRATIONS-VENDOR-ANALYSIS.md) – integrations vs. vendor
- [SESSION-QOS-RETAIN-ANALYSIS-20260303.md](SESSION-QOS-RETAIN-ANALYSIS-20260303.md) – QoS/Retain empirische Verifizierung (03.03.2026)
- [SESSION-RECORDINGS-USAGE-AND-PRELOAD-AUDIT.md](SESSION-RECORDINGS-USAGE-AND-PRELOAD-AUDIT.md) – Session-Verwendung, start-osf Default, Preload-Strategie
- [ccu-quality-fail-behaviour-2026-03.md](ccu-quality-fail-behaviour-2026-03.md) – CCU Quality-Fail: Ersatzauftrag vs. Order ERROR (Sprint 17, temporär)
