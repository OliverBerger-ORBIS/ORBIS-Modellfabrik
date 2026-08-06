# Test Coverage - Zusammenfassung

**Datum:** 2026-08-06  
**Quelle:** `npm run test:coverage` → `coverage/osf-ui/index.html`  
**Status:** Jest-Thresholds erfüllt; Langziel Lines 60 % noch offen; Branches-Langziel 40 %+ erreicht

---

## Aktuelle Coverage-Werte (osf-ui)

| Metrik | Nov 2025 (Doku) | **Aktuell** | Jest-Threshold | Langziel |
|--------|-----------------|-------------|----------------|----------|
| **Lines** | 43.84 % | **52.66 %** | 47 % ✅ | 60 %+ |
| **Branches** | 24.04 % | **46.42 %** | 30 % ✅ | 40 %+ ✅ |
| **Statements** | 43.88 % | **51.78 %** | 46 % ✅ | ~60 % |
| **Functions** | 40.81 % | **52.82 %** | 42 % ✅ | ~60 % |

**Tests:** 1388 passed / 16 skipped.

Details und Hotspots: [test-coverage-status.md](test-coverage-status.md)  
Monitoring / Schwellen: [coverage-monitoring.md](../04-howto/testing/coverage-monitoring.md)

---

## Was den Globalwert prägt

- **Stark:** Services (~80 % Lines), `workpiece-history` (~81 %), Track & Trace Component (~75 %).
- **Mittel:** Tabs (~59 %), `shopfloor-preview` (~55 %).
- **Schwach / 0 %:** viele Use-Case- und DSP-Präsentationspages (ziehen den Durchschnitt).

---

## Abgeschlossene Arbeiten (Historie Phasen 1–4)

Kurzarchiv der früheren Kampagne (Stand Doku 2025-11-30: Lines 43.84 %, Branches 24.04 %).

1. Code-Optimierungen (Memory Leaks, Build)
2. Basis-Tests (Services, Views, Tabs)
3. MessageMonitor-Refactor, Fixtures, Lazy Loading
4. Edge Cases + Integration Tests

---

## Nächste Schritte

1. Jest-Thresholds an Ist-Stand anheben (Branches ≥40, Lines näher an 50+).
2. Entscheidung: UC/DSP-Pages testen **oder** aus `collectCoverageFrom` ausschließen.
3. Kern-Shopfloor / Track & Trace Coverage bei Features mit Specs absichern.
