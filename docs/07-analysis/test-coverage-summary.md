# Test Coverage - Zusammenfassung

**Datum:** 2026-08-06 (nachmittag, UC-Specs)  
**Quelle:** `npm run test:coverage` (`--runInBand`) → `coverage/osf-ui/index.html`  
**Status:** Jest-Thresholds erfüllt; Langziel Lines **60 %+ erreicht** (64.65 %); Branches-Langziel 40 %+ erreicht

---

## Aktuelle Coverage-Werte (osf-ui)

| Metrik | Sprint-27-Ende | **Aktuell** | Jest-Threshold | Langziel |
|--------|----------------|-------------|----------------|----------|
| **Lines** | 52.66 % | **64.65 %** | 47 % ✅ | 60 %+ ✅ |
| **Branches** | 46.42 % | **48.42 %** | 30 % ✅ | 40 %+ ✅ |
| **Statements** | 51.78 % | **63.55 %** | 46 % ✅ | ~60 % ✅ |
| **Functions** | 52.82 % | **59.65 %** | 42 % ✅ | ~60 % (−0.35 %) |

**Hebung:** Use-Case SVG-Generator-Smokes (UC-01…05, 07), `applyStepToSvg`, BaseUseCase via Interoperability, Controls, Selector.

Details: [test-coverage-status.md](test-coverage-status.md) · Monitoring: [coverage-monitoring.md](../04-howto/testing/coverage-monitoring.md)

---

## Nächste Schritte (optional)

1. Jest-Thresholds anheben (Lines ≥55–60, Branches ≥40).
2. Rest: Track&Trace-UC-Shell, UC-02 Lanes, DSP-Pages.
3. Coverage immer über `npm run test:coverage` (`--runInBand`).
